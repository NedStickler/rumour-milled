from os import PathLike
from playwright.sync_api import sync_playwright
from headline_scrapers.base import BaseScraper


class YahooScraper(BaseScraper):
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_depth: int = 3,
        save_path: PathLike = ".",
    ) -> None:
        super().__init__(root, locator_strings, ignore_robots_txt, max_depth, save_path)

    def cookies(self):
        return

    def start(self):
        return


def test_playwright():
    with sync_playwright() as p:
        p.selectors.set_test_id_attribute("data-test-locator")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://news.yahoo.com/")
        page.locator("button", has_text="reject").click()
        page.wait_for_selector("a.stream-title")
        stream_item_titles = page.locator(
            '[data-test-locator="stream-item-title"]'
        ).all()
        item_titles = page.locator('[data-test-locator="item-title"]').all()
        headlines = page.locator('[data-test-locator="headline"]').all()
        hrefs = [element.get_attribute("href") for element in page.locator("a").all()]
        print(hrefs)


if __name__ == "__main__":
    yahoo_scraper = YahooScraper("https://news.yahoo.com/", [])
