import json
import asyncio
import requests
from playwright.async_api import async_playwright, TimeoutError
from os import PathLike
from validators.url import url as validate_url
from urllib.robotparser import RobotFileParser
from typing import Optional


class BaseScraper:
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        robots_txt_url: Optional[str] = None,
        ignore_robots_txt: bool = False,
        max_pages: int = 20,
        max_workers: int = 10,
        save_path: PathLike = "scraped_data.json",
        save_checkpoint: Optional[str] = None,
        headless: bool = True,
    ) -> None:
        self.root = root
        self.locator_strings = locator_strings
        self.robots_txt_url = robots_txt_url
        self.ignore_robots_txt = ignore_robots_txt
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.save_path = save_path
        self.page_number = 1
        self.page_number_lock = asyncio.Lock()
        self.queue = asyncio.Queue()
        self.visited = set()
        self.items = []
        self.save_checkpoint = save_checkpoint
        self.headless = headless
        self.failures = []
        if not self.ignore_robots_txt:
            self.robots_parser = self.setup_robots_parser(self.robots_txt_url)
        print(self.root, "DONE")

    def run(self) -> None:
        asyncio.run(self.start())

    async def start(self) -> None:
        async with async_playwright() as p:
            # Setup
            browser = await p.chromium.launch(headless=self.headless)
            self.context = await browser.new_context()
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
            self.save()

    async def deal_with_cookies(self, page) -> None:
        return

    def setup_robots_parser(self, robots_url: Optional[str] = None) -> bool:
        # Fix this monstrosity
        # RobotParser is blocking, needs custom logic. Fine for now.
        candidates = []
        candidates.append(self.root.rstrip("/") + "/robots.txt")
        if robots_url is not None:
            candidates.append(robots_url)
        for candidate in candidates:
            if self.__get_status_code(candidate) < 400:
                rp = RobotFileParser(candidate)
                rp.read()
                return rp
        raise ValueError(
            "Cannot find valid robots.txt file using robot_url or root url. Supply valid url pointing to robots.txt or set ignore_robots_txt=True"
        )

    def __get_status_code(self, url):
        try:
            res = requests.get(url)
            return res.status_code
        except Exception:
            return 400

    def can_visit(self, url: str) -> bool:
        if not url:
            return False
        valid_url = validate_url(url)
        visited = url in self.visited
        passed_robots = self.ignore_robots_txt or self.robots_parser.can_fetch("*", url)
        return valid_url and not visited and passed_robots

    async def _scrape_page(self, url: str, page) -> None:
        print(f"Scraping {url}")
        await page.goto(url, wait_until="load")
        self.visited.add(url)
        elements = await self.get_elements(page)
        hrefs = await self.get_hrefs(page)
        for element in elements:
            self.items.append(await element.inner_text())
        for href in hrefs:
            await self.queue.put(href)

    def normalise_url(self, url: str) -> str:
        if url[0] == "/":
            return self.root.rstrip("/") + url
        return url

    async def process_queue(self) -> None:
        while True:
            # Guard conditions
            async with self.page_number_lock:
                if self.page_number > self.max_pages:
                    break
            try:
                next_url = await self.queue.get()
            except asyncio.CancelledError:
                break
            next_url = self.normalise_url(next_url)
            if not self.can_visit(next_url):
                self.queue.task_done()
                continue

            # Scrape the page
            try:
                page = await self.context.new_page()
                await self._scrape_page(next_url, page)
                await page.close()
            except Exception as e:
                print(f"Failure at {next_url}: {str(e).splitlines()[0]}")
                self.failures.append((next_url, e))
            finally:
                self.queue.task_done()

            # Post-scrape admin
            async with self.page_number_lock:
                if (
                    self.save_checkpoint
                    and self.page_number % self.save_checkpoint == 0
                ):
                    self.save()
                self.page_number += 1

            await asyncio.sleep(0.5)

    async def get_elements(self, page) -> list[str]:
        elements = []
        for locator_string in self.locator_strings:
            elements += await page.locator(locator_string).all()
        return elements

    async def get_hrefs(self, page) -> list[str]:
        try:
            hrefs = await page.eval_on_selector_all(
                "a[href]", "elements => elements.map(e => e.href)"
            )
        except TimeoutError:
            print("Timed out getting href from element")
        return hrefs

    def save(self) -> None:
        print("Saving current items")
        with open(self.save_path, "w") as f:
            json.dump(self.items, f)
