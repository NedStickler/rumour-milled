import json
import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError
from os import PathLike
from pathlib import Path
from validators.url import url as validate_url
from headline_scrapers.parsers import RobotsTxtParser
from typing import Optional
from time import perf_counter


class BaseScraper:
    def __init__(
        self,
        root: Optional[str] = None,
        locator_strings: Optional[list[str]] = None,
        robots_txt_url: Optional[str] = None,
        ignore_robots_txt: Optional[bool] = None,
        max_pages: Optional[int] = None,
        max_workers: Optional[int] = None,
        save_path: Optional[PathLike] = None,
        save_checkpoint: Optional[int] = None,
        headless: Optional[bool] = None,
        user_agent: Optional[str] = None,
        config_path: Optional[PathLike] = None,
    ) -> None:
        self.config = self.load_config(config_path)

        self.root = self.get_setting(param=root, key="root", required=True)
        self.locator_strings = self.get_setting(
            param=locator_strings, key="locator_strings", required=True
        )
        self.ignore_robots_txt = self.get_setting(
            param=ignore_robots_txt, key="ignore_robots_txt", default=False
        )
        self.max_pages = self.get_setting(param=max_pages, key="max_pages", default=100)
        self.max_workers = self.get_setting(
            param=max_workers, key="max_workers", default=20
        )
        self.save_path = self.get_setting(
            param=save_path, key="save_path", default="scraped_items.json"
        )
        self.save_checkpoint = self.get_setting(
            param=save_checkpoint, key="save_checkpoint", default=10
        )
        self.headless = self.get_setting(param=headless, key="headless", default=True)
        self.user_agent = self.get_setting(
            param=user_agent, key="user_agent", default="python-requests/2.25.0"
        )

        self.page_number = 1
        self.queue = asyncio.Queue()
        self.visited = set()
        self.items = []
        self.failures = []

        self.page_number_lock = asyncio.Lock()
        self.write_lock = asyncio.Lock()
        self.visited_lock = asyncio.Lock()

        robots_txt_url = self.get_setting(param=robots_txt_url, key="robots_txt_url")
        self.robots_parser = self.setup_robots_txt_parser(robots_txt_url)
        self.logger = self.setup_logger()

    def run(self) -> None:
        start_time = perf_counter()
        asyncio.run(self.start())
        self.logger.info(
            f"Scraping completed in {perf_counter() - start_time:.2f} seconds."
        )

    async def start(self) -> None:
        async with async_playwright() as p:
            # Setup
            browser = await p.chromium.launch(headless=self.headless)
            self.context = await browser.new_context(user_agent=self.user_agent)
            page = await self.context.new_page()
            # Open root page and deal with cookies
            await page.goto(self.root, wait_until="load")
            await self.deal_with_cookies(page)
            await page.close()
            # Begin dishing out tasks
            await self.queue.put(self.root)
            async with asyncio.TaskGroup() as tg:
                for _ in range(self.max_workers):
                    tg.create_task(self.process_queue())
            await self.context.close()
            await browser.close()
            await self.save()

    async def deal_with_cookies(self, page) -> None:
        return

    def get_setting(self, param, key: str, default=None, required=False):
        if param is not None:
            return param
        if self.config and key in self.config:
            return self.config[key]
        if default is not None:
            return default
        if required:
            raise ValueError(f"Missing required config or argument: {key}")
        return None

    def load_config(self, config_path: PathLike) -> dict:
        config = {}
        if config_path:
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)
        return config

    def setup_robots_txt_parser(self, robots_txt_url: Optional[str] = None) -> bool:
        if robots_txt_url is None:
            robots_txt_url = f'{self.root.rstrip("/")}/robots.txt'
        rp = RobotsTxtParser(robots_txt_url)
        if self.ignore_robots_txt:
            rp.allow_all = True
        else:
            rp.read()
        return rp

    def setup_logger(self) -> None:
        save_folder = Path(self.save_path).parent
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"{save_folder}/scrapers.log", mode="w"),
            ],
        )
        return logging.getLogger(self.__class__.__name__)

    async def process_queue(self) -> None:
        while True:
            # Guard conditions
            async with self.page_number_lock:
                if self.page_number > self.max_pages:
                    break
                current_page_number = self.page_number
                self.page_number += 1
            try:
                next_url = await self.queue.get()
            except asyncio.CancelledError:
                break
            next_url = self.normalise_url(next_url)
            if not await self.can_visit(next_url):
                self.queue.task_done()
                continue

            # Scrape the page
            try:
                page = await self.context.new_page()
                await self.scrape_page(next_url, page)
            except Exception as e:
                self.logger.error(f"Failure at {next_url}: {str(e).splitlines()[0]}")
                self.failures.append((next_url, e))
            finally:
                await page.close()
                self.queue.task_done()

            # Save checkpoint
            if self.save_checkpoint and current_page_number % self.save_checkpoint == 0:
                await self.save()
            await asyncio.sleep(0.5)

    async def scrape_page(self, url: str, page) -> None:
        self.logger.info(f"Scraping {url}")
        await page.goto(url, wait_until="load")
        async with self.visited_lock:
            self.visited.add(url)

        elements = await self.get_elements(page)
        hrefs = await self.get_hrefs(page)

        elements_text = []
        for element in elements:
            elements_text.append(await element.inner_text())
        for href in hrefs:
            await self.queue.put(href)
        async with self.write_lock:
            self.items.extend(elements_text)

    async def can_visit(self, url: str) -> bool:
        valid_url = validate_url(url)
        async with self.visited_lock:
            visited = url in self.visited
        passed_robots = self.robots_parser.can_fetch("*", url)
        return valid_url and not visited and passed_robots

    def normalise_url(self, url: str) -> str:
        if url[0] == "/":
            return self.root.rstrip("/") + url
        return url

    async def get_elements(self, page) -> list[str]:
        elements = []
        for locator_string in self.locator_strings:
            elements += await page.locator(locator_string).all()
        return elements

    async def get_hrefs(self, page) -> list[str]:
        hrefs = await page.eval_on_selector_all(
            "a[href]", "elements => elements.map(e => e.href)"
        )
        return hrefs

    async def save(self) -> None:
        async with self.write_lock:
            self.logger.info("Saving current items")
            if not Path(self.save_path).exists():
                with open(self.save_path, "w") as f:
                    json.dump([], f)
            with open(self.save_path, "r+") as f:
                existing_data = json.load(f)
                f.seek(0)
                f.truncate()
                json.dump(existing_data + self.items, f)
            self.items.clear()
