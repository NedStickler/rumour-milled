import json
import asyncio
import logging
from playwright.async_api import async_playwright
from os import PathLike
from pathlib import Path
from validators.url import url as validate_url
from headline_scrapers.parsers import RobotsTxtParser
from typing import Optional
from time import perf_counter


class BaseScraper:
    """Base class for concurrent web scraping using Playwright and asyncio.

    This class provides a configurable framework for scraping web pages concurrently, handling navigation, queueing, robots.txt compliance, and saving scraped data. Supports configuration via arguments or YAML config file.

    Args:
        root (str, optional): The root URL to start scraping from.
        locator_strings (list[str], optional): List of CSS/XPath selectors to locate elements to scrape.
        robots_txt_url (str, optional): URL to a robots.txt file. If None, will try root + '/robots.txt'.
        ignore_robots_txt (bool, optional): If True, robots.txt rules are ignored. Defaults to False.
        max_pages (int, optional): Maximum number of pages to scrape. Defaults to 100.
        max_workers (int, optional): Number of concurrent workers. Defaults to 20.
        save_path (PathLike, optional): Path to save scraped items. Defaults to 'scraped_items.json'.
        save_checkpoint (int, optional): Save after this many pages. Defaults to 10.
        headless (bool, optional): Whether to run browser in headless mode. Defaults to True.
        user_agent (str, optional): User agent string for browser. Defaults to 'python-requests/2.25.0'.
        config_path (PathLike, optional): Path to YAML config file for scraper settings.

    Attributes:
        config (dict): Loaded configuration from YAML file (if provided).
        root (str): The root URL.
        locator_strings (list[str]): List of selectors for scraping.
        ignore_robots_txt (bool): Whether to ignore robots.txt.
        max_pages (int): Max pages to scrape.
        max_workers (int): Number of concurrent workers.
        save_path (PathLike): Path to save data.
        save_checkpoint (int): Save checkpoint interval.
        headless (bool): Headless browser flag.
        user_agent (str): User agent string.
        page_number (int): Current page number.
        queue (asyncio.Queue): Queue of URLs to visit.
        visited (set): Set of visited URLs.
        items (list): List of scraped items.
        failures (list): List of (url, exception) tuples for failed pages.
        page_number_lock (asyncio.Lock): Lock for page number updates.
        write_lock (asyncio.Lock): Lock for writing items.
        visited_lock (asyncio.Lock): Lock for updating visited URLs.
        robots_parser (RobotsTxtParser): Parser for robots.txt.
        logger (logging.Logger): Logger for scraper events.
    """

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
        """Initialize the BaseScraper with configuration from arguments or YAML file.

        Args:
            root (Optional[str]): The root URL to start scraping from.
            locator_strings (Optional[list[str]]): List of CSS/XPath selectors to locate elements to scrape.
            robots_txt_url (Optional[str]): URL to a robots.txt file.
            ignore_robots_txt (Optional[bool]): If True, robots.txt rules are ignored.
            max_pages (Optional[int]): Maximum number of pages to scrape.
            max_workers (Optional[int]): Number of concurrent workers.
            save_path (Optional[PathLike]): Path to save scraped items.
            save_checkpoint (Optional[int]): Save after this many pages.
            headless (Optional[bool]): Whether to run browser in headless mode.
            user_agent (Optional[str]): User agent string for browser.
            config_path (Optional[PathLike]): Path to YAML config file for scraper settings.
        """
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
        """Run the scraper asynchronously."""
        start_time = perf_counter()
        asyncio.run(self.start())
        self.logger.info(
            f"Scraping completed in {perf_counter() - start_time:.2f} seconds."
        )

    async def start(self) -> None:
        """Start the asynchronous scraping process, launching browser and workers."""
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
        """Handle cookie consent dialogs or banners if needed. Override in subclasses for custom logic.

        Args:
            page: Playwright page object.
        """
        return

    def get_setting(self, param, key: str, default=None, required=False):
        """Get a configuration setting from argument, config file, or default value.

        Args:
            param: The parameter value provided directly.
            key (str): The config key to look up.
            default: Default value if not provided.
            required (bool): Whether the setting is required.

        Returns:
            The resolved setting value.
        """
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
        """Load scraper configuration from a YAML file if provided.

        Args:
            config_path (PathLike): Path to the YAML config file.

        Returns:
            dict: Loaded configuration dictionary.
        """
        config = {}
        if config_path:
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)
        return config

    def setup_robots_txt_parser(self, robots_txt_url: Optional[str] = None) -> bool:
        """Set up the robots.txt parser for the scraper.

        Args:
            robots_txt_url (Optional[str]): URL to robots.txt file.

        Returns:
            RobotsTxtParser: Configured robots.txt parser.
        """
        if robots_txt_url is None:
            robots_txt_url = f'{self.root.rstrip("/")}/robots.txt'
        rp = RobotsTxtParser(robots_txt_url)
        if self.ignore_robots_txt:
            rp.allow_all = True
        else:
            rp.read()
        return rp

    def setup_logger(self) -> None:
        """Set up a logger for the scraper, logging to both console and file.

        Returns:
            logging.Logger: Configured logger instance.
        """
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
        """Process the queue of URLs to scrape, handling concurrency and checkpoints."""
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
        """Scrape a single page, extract elements and hrefs, and add new URLs to the queue.

        Args:
            url (str): URL of the page to scrape.
            page: Playwright page object.
        """
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
        """Check if a URL can be visited (valid, not visited, allowed by robots.txt).

        Args:
            url (str): URL to check.

        Returns:
            bool: True if the URL can be visited, False otherwise.
        """
        valid_url = validate_url(url)
        async with self.visited_lock:
            visited = url in self.visited
        passed_robots = self.robots_parser.can_fetch("*", url)
        return valid_url and not visited and passed_robots

    def normalise_url(self, url: str) -> str:
        """Normalise relative URLs to absolute URLs based on root.

        Args:
            url (str): URL to normalise.

        Returns:
            str: Normalised absolute URL.
        """
        if url[0] == "/":
            return self.root.rstrip("/") + url
        return url

    async def get_elements(self, page) -> list[str]:
        """Get elements matching the locator strings on the current page.

        Args:
            page: Playwright page object.

        Returns:
            list[str]: List of element handles matching the locator strings.
        """
        elements = []
        for locator_string in self.locator_strings:
            elements += await page.locator(locator_string).all()
        return elements

    async def get_hrefs(self, page) -> list[str]:
        """Get href attributes from all anchor tags on the current page.

        Args:
            page: Playwright page object.

        Returns:
            list[str]: List of href URLs found on the page.
        """
        hrefs = await page.eval_on_selector_all(
            "a[href]", "elements => elements.map(e => e.href)"
        )
        return hrefs

    async def save(self) -> None:
        """Save the scraped items to the specified save_path as JSON, appending to existing data."""
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
