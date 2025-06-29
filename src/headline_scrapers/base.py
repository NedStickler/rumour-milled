from playwright.sync_api import sync_playwright, TimeoutError
from queue import SimpleQueue
from os import PathLike
from validators.url import url
import json


class BaseScraper:
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_pages: int = 3,
        save_path: PathLike = ".",
        save_checkpont: int = None,
    ) -> None:
        self.root = root
        self.locator_strings = locator_strings
        self.ignore_robots_txt = ignore_robots_txt
        self.max_pages = max_pages
        self.save_path = save_path
        self.page_number = 0
        self.queue = SimpleQueue()
        self.visited = []
        self.items = []
        self.save_checkpoint = save_checkpont

    def start(self) -> None:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            self.page = context.new_page()
            self.page.goto(self.root, wait_until="load")
            self.deal_with_cookies()
            self.process_queue()
            self.save()

    def deal_with_cookies(self) -> None:
        return

    def process_queue(self) -> None:
        self.queue.put(self.root)
        while not self.queue.empty() and self.page_number < self.max_pages:
            next_page = self.queue.get()

            if next_page in self.visited:
                continue
            if len(next_page) == 0:
                continue
            if next_page[0] == "/":
                next_page = self.root + next_page
            if url(next_page) is not True:
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

            if (
                not self.save_checkpoint is None
                and self.page_number % self.save_checkpoint == 0
            ):
                self.save()
            self.page_number += 1

    def get_elements(self) -> list[str]:
        elements = []
        for locator_string in self.locator_strings:
            elements += self.page.locator(locator_string).all()
        return elements

    def get_hrefs(self) -> list[str]:
        hrefs = []
        for a in self.page.locator("a").all():
            try:
                hrefs.append(a.get_attribute("href"))
            except TimeoutError:
                print("Timed out getting href from element")
        return hrefs

    def save(self) -> None:
        with open(self.save_path, "w") as f:
            json.dump(self.items, f)
