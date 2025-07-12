import json
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from os import PathLike
from pathlib import Path
from validators.url import url as validate_url
from headline_scrapers.parsers import RobotsTxtParser
from typing import Optional


class BaseScraper:
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        robots_txt_url: Optional[str] = None,
        ignore_robots_txt: bool = False,
        max_pages: int = 1000,
        max_workers: int = 20,
        save_path: PathLike = "scraped_data.json",
        save_checkpoint: Optional[str] = None,
        headless: bool = True,
    ) -> None:
        self.root = root
        self.locator_strings = locator_strings
        self.ignore_robots_txt = ignore_robots_txt
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.save_path = save_path
        self.page_number = 1
        self.page_number_lock = asyncio.Lock()
        self.write_lock = asyncio.Lock()
        self.queue = asyncio.Queue()
        self.visited = set()
        self.items = []
        self.save_checkpoint = save_checkpoint
        self.headless = headless
        self.failures = []
        self.robots_parser = self.setup_robots_txt_parser(robots_txt_url)

    def run(self) -> None:
        asyncio.run(self.start())

    async def start(self) -> None:
        async with async_playwright() as p:
            # Setup
            browser = await p.chromium.launch(headless=self.headless)
            self.context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            )
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

    def setup_robots_txt_parser(self, robots_txt_url: Optional[str] = None) -> bool:
        if robots_txt_url is None:
            robots_txt_url = self.root.rstrip("/") + "/robots.txt"
        rp = RobotsTxtParser(robots_txt_url)
        if self.ignore_robots_txt:
            rp.allow_all = True
        else:
            rp.read()
        return rp

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
            if not self.can_visit(next_url):
                self.queue.task_done()
                continue

            # Scrape the page
            try:
                page = await self.context.new_page()
                await self.scrape_page(next_url, page)
            except Exception as e:
                print(f"Failure at {next_url}: {str(e).splitlines()[0]}")
                self.failures.append((next_url, e))
            finally:
                await page.close()
                self.queue.task_done()

            # Save checkpoint
            if self.save_checkpoint and current_page_number % self.save_checkpoint == 0:
                await self.save()
            await asyncio.sleep(0.5)

    async def scrape_page(self, url: str, page) -> None:
        print(f"Scraping {url}")
        await page.goto(url, wait_until="load")
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

    def can_visit(self, url: str) -> bool:
        valid_url = validate_url(url)
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
        try:
            hrefs = await page.eval_on_selector_all(
                "a[href]", "elements => elements.map(e => e.href)"
            )
        except TimeoutError:
            print("Timed out getting href from element")
        return hrefs

    async def save(self) -> None:
        async with self.write_lock:
            print("Saving current items")
            if not Path(self.save_path).exists():
                with open(self.save_path, "w") as f:
                    json.dump([], f)
            with open(self.save_path, "r+") as f:
                existing_data = json.load(f)
                f.seek(0)
                f.truncate()
                json.dump(existing_data + self.items, f)
            self.items.clear()
