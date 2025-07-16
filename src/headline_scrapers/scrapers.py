from headline_scrapers.base import BaseScraper
from playwright.sync_api import TimeoutError


class YahooScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://news.yahoo.com", **kwargs)

    async def deal_with_cookies(self, page) -> None:
        await page.get_by_role("button", name="reject").click()
        await page.wait_for_load_state()


class SkyScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://news.sky.com", **kwargs)


class CBCScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.cbc.ca", **kwargs)

    async def deal_with_cookies(self, page) -> None:
        try:
            await page.get_by_role("button", name="manage").click()
            await page.wait_for_load_state()
            await page.get_by_role("button", name="Confirm choices").click()
            await page.wait_for_load_state()
        except TimeoutError:
            self.logger.error("Failed to find cookies management")


class ABCScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.abc.net.au", **kwargs)


class FoxScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.foxnews.com", **kwargs)


class NBCScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.nbcnews.com", **kwargs)

    async def deal_with_cookies(self, page):
        try:
            await page.get_by_role("button", name="Continue").click()
            await page.wait_for_load_state()
        except TimeoutError:
            self.logger.error("Failed to find cookies management")


class IrishTimesScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.irishtimes.com", **kwargs)

    async def deal_with_cookies(self, page):
        await page.get_by_role("button", name="manage").click()
        await page.wait_for_load_state()
        await page.get_by_role("button", name="reject").click()
        await page.wait_for_load_state()


class BusinessTechScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://businesstech.co.za", **kwargs)


class RNZScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.rnz.co.nz", **kwargs)


class HeraldScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(root="https://www.heraldscotland.com", **kwargs)

    async def deal_with_cookies(self, page) -> None:
        try:
            await page.get_by_role("button", name="Reject All").click()
            await page.wait_for_load_state()
            await page.get_by_role("button", name="READ FOR FREE").click()
            await page.wait_for_load_state()
        except TimeoutError:
            self.logger.error("Failed to find cookies management")
