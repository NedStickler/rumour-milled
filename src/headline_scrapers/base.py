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
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        robots_txt_url: str | None = None,
        ignore_robots_txt: bool = False,
        max_pages: int = 3,
        save_path: PathLike = ".",
        save_checkpont: int = None,
        headless: bool = True,
    ) -> None:
        self.root = root
        self.locator_strings = locator_strings
        self.ignore_robots_txt = ignore_robots_txt
        self.max_pages = max_pages
        self.save_path = save_path
        self.page_number = 1
        self.queue = SimpleQueue()
        self.visited = []
        self.items = []
        self.save_checkpoint = save_checkpont
        self.headless = headless
        self.failures = []
        if not ignore_robots_txt:
            self.robots_parser = self.setup_robots_parser(robots_txt_url)

    def start(self) -> None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            self.page = context.new_page()
            self.page.goto(self.root, wait_until="load")
            self.deal_with_cookies()
            self.process_queue()
            self.save()

    def deal_with_cookies(self) -> None:
        return

    def setup_robots_parser(self, robots_url: str | None) -> bool:
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
        try:
            return requests.get(url).status_code
        except requests.exceptions.RequestException:
            return 400

    def process_queue(self) -> None:
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
        elements = []
        for locator_string in self.locator_strings:
            elements += self.page.locator(locator_string).all()
        return elements

    def get_hrefs(self) -> list[str]:
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
        print("Saving current items")
        with open(self.save_path, "w") as f:
            json.dump(self.items, f)
