from headline_scrapers.base import BaseScraper
from typing import Optional


class HeadlineScraper(BaseScraper):
    def __init__(
        self, root: str, locator_strings: list[str], **kwargs: Optional[str]
    ) -> None:
        super().__init__(root, locator_strings, **kwargs)


class TestYahooScraper(HeadlineScraper):
    def __init__(
        self,
        **kwargs: Optional[str],
    ) -> None:
        super().__init__(
            root="https://news.yahoo.com",
            locator_strings=[
                '[data-test-locator="headline"]',
                '[data-test-locator="item-title"]',
                '[data-test-locator="stream-item-title"]',
                '[class*="headline"]',
            ],
            **kwargs,
        )

    async def deal_with_cookies(self, page) -> None:
        await page.locator("button", has_text="reject").click()
        await page.wait_for_load_state()


if __name__ == "__main__":
    yahoo_scraper = TestYahooScraper(
        max_pages=20,
        max_workers=20,
        robots_txt_url="https://news.yahoo.com/robots.txt",
        save_path="data/raw/scraped_yahoo_headlines.json",
    )
    yahoo_scraper.run()
