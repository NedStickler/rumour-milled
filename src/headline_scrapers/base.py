from playwright.sync_api import sync_playwright, TimeoutError
from queue import SimpleQueue
from os import PathLike
from validators.url import url
import json
import requests
from urllib.robotparser import RobotFileParser


# TODO:
# - Point of diminishing return?
# - Fix gross ignore robots.txt logic
# - DOCUMENT!


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
        robots_txt_url: str | None = None,
        ignore_robots_txt: bool = False,
        max_pages: int = 100,
        save_path: PathLike = ".",
        save_checkpoint: int = None,
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
        self.ignore_robots_txt = ignore_robots_txt
        self.max_pages = max_pages
        self.save_path = save_path
        self.page_number = 1
        self.queue = SimpleQueue()
        self.visited = []
        self.items = []
        self.save_checkpoint = save_checkpoint
        self.headless = headless
        self.failures = []
        if not ignore_robots_txt:
            self.robots_parser = self.setup_robots_parser(robots_txt_url)

    def start(self) -> None:
        """Start the scraping process.

        Launches a Playwright browser, navigates to the root URL, handles cookies, processes the scraping queue, and saves the results.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            self.page = context.new_page()
            self.page.goto(self.root, wait_until="load")
            self.deal_with_cookies()
            self.process_queue()
            self.save()

    def deal_with_cookies(self) -> None:
        """Handle cookie consent dialogs or banners if needed.

        Override this method in subclasses to implement custom cookie handling logic.
        """
        return

    def setup_robots_parser(self, robots_url: str | None) -> bool:
        """Set up the robots.txt parser for the scraper.

        Tries to use the provided robots.txt URL, or falls back to root + '/robots.txt'.
        Raises ValueError if no valid robots.txt is found.

        Args:
            robots_url (str | None): URL to robots.txt file.

        Returns:
            RobotFileParser: Configured robots.txt parser.
        """
        user_code = self.__get_status_code(robots_url)
        root_code = self.__get_status_code(self.root + "/robots.txt")
        if user_code < 400:
            rp = RobotFileParser(robots_url)
            rp.read()
            return rp
        if root_code < 400:
            rp = RobotFileParser(self.root + "/robots.txt")
            rp.read()
            return rp
        raise ValueError(
            "Cannot find valid robots.txt file using robot_url or root url. Supply valid url pointing to robots.txt or set ignore_robots_txt=False"
        )

    def __get_status_code(self, url):
        """Get the HTTP status code for a given URL.

        Args:
            url (str): The URL to check.

        Returns:
            int: HTTP status code, or 400 if request fails.
        """
        try:
            return requests.get(url).status_code
        except requests.exceptions.RequestException:
            return 400

    def process_queue(self) -> None:
        """Process the queue of URLs to scrape.

        Visits each URL in the queue, scrapes elements and links, respects robots.txt, and saves data at checkpoints.
        """
        self.queue.put(self.root)
        while not self.queue.empty() and self.page_number < self.max_pages + 1:
            try:
                next_page = self.queue.get()
                if len(next_page) == 0:
                    continue
                if next_page[0] == "/":
                    next_page = self.root + next_page
                if url(next_page) is not True:
                    continue
                if next_page in self.visited:
                    continue
                if not self.ignore_robots_txt and not self.robots_parser.can_fetch(
                    "*", next_page
                ):
                    print(f"Skipping {next_page} due to robots.txt disallow")
                    continue

                print(f"({self.page_number}) Scraping {next_page}")
                self.page.goto(next_page, wait_until="load")
                self.visited.append(next_page)

                elements = self.get_elements()
                hrefs = self.get_hrefs()
                for element in elements:
                    self.items.append(element.inner_text())
                for href in hrefs:
                    self.queue.put(href)

                if self.save_checkpoint == 1 or (
                    self.save_checkpoint is not None
                    and self.page_number != 0
                    and self.page_number % self.save_checkpoint == 0
                ):
                    self.save()
                self.page_number += 1
            except Exception as e:
                print(f"Failure at {next_page}")
                self.failures.append((next_page, e))

    def get_elements(self) -> list[str]:
        """Get elements matching the locator strings on the current page.

        Returns:
            list[str]: List of Playwright element handles matching the locator strings.
        """
        elements = []
        for locator_string in self.locator_strings:
            elements += self.page.locator(locator_string).all()
        return elements

    def get_hrefs(self) -> list[str]:
        """Get href attributes from all anchor tags on the current page.

        Returns:
            list[str]: List of href URLs found on the page.
        """
        hrefs = []
        fail_count = 0
        for a in self.page.locator("a").all():
            if fail_count == 5:
                break
            try:
                hrefs.append(a.get_attribute("href"))
            except TimeoutError:
                print("Timed out getting href from element")
                fail_count += 1
        return hrefs

    def save(self) -> None:
        """Save the scraped items to the specified save_path as JSON."""
        print("Saving current items")
        with open(self.save_path, "w") as f:
            json.dump(self.items, f)
