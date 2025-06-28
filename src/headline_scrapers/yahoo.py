from os import PathLike
from playwright.sync_api import sync_playwright
from headline_scrapers.base import BaseScraper


class YahooScraper(BaseScraper):
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_pages: int = 3,
        save_path: PathLike = ".",
    ) -> None:
        super().__init__(root, locator_strings, ignore_robots_txt, max_pages, save_path)

    def deal_with_cookies(self) -> None:
        self.page.goto(self.root, wait_until="load")
        self.page.locator("button", has_text="reject").click()


if __name__ == "__main__":
    yahoo_scraper = YahooScraper(
        "https://news.yahoo.com/",
        [
            '[data-test-locator="headline"]',
            '[data-test-locator="item-title"]',
            '[data-test-locator="stream-item-title"]',
        ],
        max_pages=50,
        save_path="data/raw/scraped_yahoo_headlines.json",
    )
    yahoo_scraper.start()
