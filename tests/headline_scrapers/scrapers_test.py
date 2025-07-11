from headline_scrapers.base import BaseScraper
from os import PathLike


class TestScraper(BaseScraper):
    def __init__(
        self,
        locator_strings: list[str],
        robots_txt_url: str | None = None,
        ignore_robots_txt: bool = False,
        max_pages: int = 500,
        save_path: PathLike = ".",
        save_checkpoint: int | None = 10,
        headless: bool = True,
    ) -> None:
        super().__init__(
            "https://news.yahoo.com",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    async def deal_with_cookies(self, page) -> None:
        await page.locator("button", has_text="reject").click()
        await page.wait_for_load_state()


if __name__ == "__main__":
    yahoo_scraper = TestScraper(
        locator_strings=[
            '[data-test-locator="headline"]',
            '[data-test-locator="item-title"]',
            '[data-test-locator="stream-item-title"]',
            '[class*="headline"]',
        ],
        max_pages=100,
        robots_txt_url="https://news.yahoo.com/robots.txt",
        ignore_robots_txt=False,
        save_path="data/raw/scraped_yahoo_headlines.json",
    )
    yahoo_scraper.run()
