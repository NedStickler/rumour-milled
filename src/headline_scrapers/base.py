from playwright.async_api import async_playwright, TimeoutError
from queue import SimpleQueue
from os import PathLike
from validators.url import url as validate_url
import json
import requests
import aiofiles
import asyncio
import aiohttp
from urllib.robotparser import RobotFileParser
from typing import Optional


# TODO:
# - Point of diminishing return?
# - Fix gross ignore robots.txt logic


class BaseScraper:
    """Base class for web scrapers using Playwright.

    Pprovides a framework for scraping web pages, handling navigation, queueing, robots.txt compliance, and saving scraped data.

    Args:
        root (str): The root URL to start scraping from.
        locator_strings (list[str]): List of CSS/XPath selectors to locate elements to scrape.
        robots_txt_url (str | None, optional): URL to a robots.txt file. If None, will try root + '/robots.txt'.
        ignore_robots_txt (bool, optional): If True, robots.txt rules are ignored. Defaults to False.
        max_pages (int, optional): Maximum number of pages to scrape. Defaults to 100.
        save_path (PathLike, optional): Path to save scraped items. Defaults to current directory.
        save_checkpoint (int, optional): Save after this many pages. If None, only saves at end. Defaults to None.
        headless (bool, optional): Whether to run browser in headless mode. Defaults to True.

    Attributes:
        root (str): The root URL.
        locator_strings (list[str]): List of selectors for scraping.
        ignore_robots_txt (bool): Whether to ignore robots.txt.
        max_pages (int): Max pages to scrape.
        save_path (PathLike): Path to save data.
        page_number (int): Current page number.
        queue (SimpleQueue): Queue of URLs to visit.
        visited (list): List of visited URLs.
        items (list): List of scraped items.
        save_checkpoint (int | None): Save checkpoint interval.
        headless (bool): Headless browser flag.
        failures (list): List of (url, exception) tuples for failed pages.
        robots_parser (RobotFileParser): Parser for robots.txt (if not ignored).
    """

    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        robots_txt_url: Optional[str] = None,
        ignore_robots_txt: bool = False,
        max_pages: int = 100,
        save_path: PathLike = ".",
        save_checkpoint: Optional[str] = None,
        headless: bool = True,
    ) -> None:
        """Initialize the BaseScraper instance.

        Args:
            root (str): The root URL to start scraping from.
            locator_strings (list[str]): List of CSS/XPath selectors to locate elements to scrape.
            robots_txt_url (str | None, optional): URL to a robots.txt file. If None, will try root + '/robots.txt'.
            ignore_robots_txt (bool, optional): If True, robots.txt rules are ignored. Defaults to False.
            max_pages (int, optional): Maximum number of pages to scrape. Defaults to 100.
            save_path (PathLike, optional): Path to save scraped items. Defaults to current directory.
            save_checkpoint (int, optional): Save after this many pages. If None, only saves at end. Defaults to None.
            headless (bool, optional): Whether to run browser in headless mode. Defaults to True.
        """
        self.root = root
        self.locator_strings = locator_strings
        self.robots_txt_url = robots_txt_url
        self.ignore_robots_txt = ignore_robots_txt
        self.max_pages = max_pages
        self.save_path = save_path
        self.page_number = 1
        self.queue = asyncio.Queue()
        self.visited = []
        self.items = []
        self.save_checkpoint = save_checkpoint
        self.headless = headless
        self.failures = []

    def run(self) -> None:
        asyncio.run(self.start())

    async def start(self) -> None:
        """Start the scraping process.

        Launches a Playwright browser, navigates to the root URL, handles cookies, processes the scraping queue, and saves the results.
        """
        self.robots_parser = await self.setup_robots_parser(self.robots_txt_url)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            self.context = await browser.new_context()
            page = await self.context.new_page()
            await page.goto(self.root, wait_until="load")
            await self.deal_with_cookies(page)
            await self.process_queue()
            self.save()

    async def deal_with_cookies(self, page) -> None:
        """Handle cookie consent dialogs or banners if needed.

        Override this method in subclasses to implement custom cookie handling logic.
        """
        return

    async def setup_robots_parser(self, robots_url: Optional[str] = None) -> bool:
        """Set up the robots.txt parser for the scraper.

        Tries to use the provided robots.txt URL, or falls back to root + '/robots.txt'.
        Raises ValueError if no valid robots.txt is found.

        Args:
            robots_url (str | None): URL to robots.txt file.

        Returns:
            RobotFileParser: Configured robots.txt parser.
        """
        candidates = []
        candidates.append(self.root.rstrip("/") + "/robots.txt")
        if robots_url is not None:
            candidates.append(robots_url)
        for candidate in candidates:
            if await self.__get_status_code(candidate) < 400:
                rp = RobotFileParser(candidate)
                rp.read()
                return rp
        raise ValueError(
            "Cannot find valid robots.txt file using robot_url or root url. Supply valid url pointing to robots.txt or set ignore_robots_txt=False"
        )

    async def __get_status_code(self, url):
        """Get the HTTP status code for a given URL.

        Args:
            url (str): The URL to check.

        Returns:
            int: HTTP status code, or 400 if request fails.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return response.status
        except Exception:
            return 400

    def _can_vist(self, url: str) -> bool:
        if url[0] == "/":
            url = self.root.rstrip("/") + url
        valid_url = validate_url(url)
        visited = url in self.visited
        passed_robots = self.ignore_robots_txt or self.robots_parser.can_fetch("*", url)
        return valid_url and not visited and passed_robots

    async def _scrape_page(self, url: str) -> None:
        """Scrape a single URL.

        Visits the URL, scrapes elements and links, and saves data at checkpoints.
        This method is called by process_queue() for each URL in the queue.
        """
        if not url or not self._can_vist(url):
            return

        print(f"Scraping {url}")

        page = await self.context.new_page()
        await page.goto(url, wait_until="load")
        self.visited.append(url)

        elements = await self.get_elements(page)
        hrefs = await self.get_hrefs(page)

        for element in elements:
            self.items.append(await element.inner_text())
        for href in hrefs:
            await self.queue.put(href)

        if self.save_checkpoint and self.page_number % self.save_checkpoint == 0:
            await self.save()

    async def process_queue(self) -> None:
        """Process the queue of URLs to scrape.

        Visits each URL in the queue, scrapes elements and links, respects robots.txt, and saves data at checkpoints.
        """
        await self.queue.put(self.root)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent tasks
        while not self.queue.empty() and self.page_number <= self.max_pages:

            async def task():
                async with semaphore:
                    try:
                        next_page = await self.queue.get()
                        await self._scrape_page(next_page)
                    except Exception as e:
                        print(f"Failure at {next_page}: {e}")
                        self.failures.append((next_page, e))

            self.page_number += 1
        tasks = [asyncio.create_task(task()) for _ in range(self.max_pages)]
        await asyncio.gather(*tasks)

    async def get_elements(self, page) -> list[str]:
        """Get elements matching the locator strings on the current page.

        Returns:
            list[str]: List of Playwright element handles matching the locator strings.
        """
        elements = []
        for locator_string in self.locator_strings:
            elements += await page.locator(locator_string).all()
        return elements

    async def get_hrefs(self, page) -> list[str]:
        """Get href attributes from all anchor tags on the current page.

        Returns:
            list[str]: List of href URLs found on the page.
        """
        hrefs = []
        fail_count = 0
        for a in await page.locator("a").all():
            if fail_count == 5:
                break
            try:
                hrefs.append(await a.get_attribute("href"))
            except TimeoutError:
                print("Timed out getting href from element")
                fail_count += 1
        return hrefs

    def save(self) -> None:
        """Save the scraped items to the specified save_path as JSON."""
        print("Saving current items")
        with open(self.save_path, "w") as f:
            json.dump(self.items, f)
