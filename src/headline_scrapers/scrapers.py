from os import PathLike
from headline_scrapers.base import BaseScraper
from playwright.sync_api import TimeoutError
from typing import Optional


class YahooScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
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
        await page.get_by_role("button", name="reject").click()
        await page.wait_for_load_state()


class SkyScraper(BaseScraper):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__(
            root="https://news.sky.com",
            locator_strings=['[class*="headline"]'],
            **kwargs,
        )


class CBCScraper(BaseScraper):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__(
            root="https://www.cbc.ca", locator_strings=['[class*="headline"]'], **kwargs
        )

    async def deal_with_cookies(self, page) -> None:
        await page.get_by_role("button", name="manage").click()
        await page.wait_for_load_state()
        await page.get_by_role("button", name="Confirm choices").click()
        await page.wait_for_load_state()


class ABCScraper(BaseScraper):
    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__(
            root="https://www.abc.net.au",
            locator_strings=['[data-component*="CardHeading"]'],
            **kwargs,
        )


class FoxScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            root="https://www.foxnews.com",
            locator_strings=['[class*="title"]'],
            **kwargs,
        )


class NBCScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            root="https://www.nbcnews.com",
            locator_strings=['[class*="headline"]'],
            **kwargs,
        )

    async def deal_with_cookies(self, page):
        await page.get_by_role("button", name="Continue").click()
        await page.wait_for_load_state()


class IrishTimesScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            root="https://www.irishtimes.com",
            locator_strings=['[class*="heading"]'],
            **kwargs,
        )

    async def deal_with_cookies(self, page):
        await page.get_by_role("button", name="manage").click()
        await page.wait_for_load_state()
        await page.get_by_role("button", name="reject").click()
        await page.wait_for_load_state()


class BusinessTechScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            root="https://businesstech.co.za",
            locator_strings=['[class*="entry-title"]'],
            **kwargs,
        )


class RNZScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            root="https://www.rnz.co.nz",
            locator_strings=['[class*="headline"]'],
            **kwargs,
        )


class HeraldScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            root="https://www.heraldscotland.com",
            locator_strings=['[class*="headline"]'],
            **kwargs,
        )

    async def deal_with_cookies(self, page) -> None:
        try:
            await page.get_by_role("button", name="Reject All").click()
            await page.wait_for_load_state()
            await page.get_by_role("button", name="READ FOR FREE").click()
            await page.wait_for_load_state()
        except TimeoutError:
            print("Failed to find cookies management")
