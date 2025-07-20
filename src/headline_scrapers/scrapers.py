from headline_scrapers.base import BaseScraper
from storage.storage import HeadlineStore
from playwright.sync_api import TimeoutError


class HeadlineScraper(BaseScraper):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.headline_storage = HeadlineStore()

    async def save(self) -> None:
        async with self.write_lock:
            items = [{"headline": headline, "label": 0} for headline in self.items]
            self.headline_storage.put_items(items)
            self.items.clear()


class YahooScraper(HeadlineScraper):
    """Scraper for Yahoo News headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize YahooScraper with Yahoo News as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://news.yahoo.com", **kwargs)

    async def deal_with_cookies(self, page) -> None:
        """Handle Yahoo's cookie consent dialog by clicking the 'reject' button.

        Args:
            page: Playwright page object.
        """
        await page.get_by_role("button", name="reject").click()
        await page.wait_for_load_state()


class SkyScraper(HeadlineScraper):
    """Scraper for Sky News headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize SkyScraper with Sky News as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://news.sky.com", **kwargs)


class CBCScraper(HeadlineScraper):
    """Scraper for CBC News headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize CBCScraper with CBC News as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.cbc.ca", **kwargs)

    async def deal_with_cookies(self, page) -> None:
        """Handle CBC's cookie consent dialog by clicking the appropriate buttons.

        Args:
            page: Playwright page object.
        """
        try:
            await page.get_by_role("button", name="manage").click()
            await page.wait_for_load_state()
            await page.get_by_role("button", name="Confirm choices").click()
            await page.wait_for_load_state()
        except TimeoutError:
            self.logger.error("Failed to find cookies management")


class ABCScraper(HeadlineScraper):
    """Scraper for ABC News headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize ABCScraper with ABC News as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.abc.net.au", **kwargs)


class FoxScraper(HeadlineScraper):
    """Scraper for Fox News headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize FoxScraper with Fox News as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.foxnews.com", **kwargs)


class NBCScraper(HeadlineScraper):
    """Scraper for NBC News headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize NBCScraper with NBC News as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.nbcnews.com", **kwargs)

    async def deal_with_cookies(self, page):
        """Handle NBC's cookie consent dialog by clicking the 'Continue' button.

        Args:
            page: Playwright page object.
        """
        try:
            await page.get_by_role("button", name="Continue").click()
            await page.wait_for_load_state()
        except TimeoutError:
            self.logger.error("Failed to find cookies management")


class IrishTimesScraper(HeadlineScraper):
    """Scraper for Irish Times headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize IrishTimesScraper with Irish Times as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.irishtimes.com", **kwargs)

    async def deal_with_cookies(self, page):
        """Handle Irish Times' cookie consent dialog by clicking the 'manage' and 'reject' buttons.

        Args:
            page: Playwright page object.
        """
        await page.get_by_role("button", name="manage").click()
        await page.wait_for_load_state()
        await page.get_by_role("button", name="reject").click()
        await page.wait_for_load_state()


class BusinessTechScraper(HeadlineScraper):
    """Scraper for BusinessTech headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize BusinessTechScraper with BusinessTech as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://businesstech.co.za", **kwargs)


class RNZScraper(HeadlineScraper):
    """Scraper for RNZ headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize RNZScraper with RNZ as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.rnz.co.nz", **kwargs)


class HeraldScraper(HeadlineScraper):
    """Scraper for Herald Scotland headlines."""

    def __init__(self, **kwargs) -> None:
        """Initialize HeraldScraper with Herald Scotland as the root URL.

        Args:
            **kwargs: Additional keyword arguments for BaseScraper.
        """
        super().__init__(root="https://www.heraldscotland.com", **kwargs)

    async def deal_with_cookies(self, page) -> None:
        """Handle Herald Scotland's cookie consent dialog by clicking the 'Reject All' and 'READ FOR FREE' buttons.

        Args:
            page: Playwright page object.
        """
        try:
            await page.get_by_role("button", name="Reject All").click()
            await page.wait_for_load_state()
            await page.get_by_role("button", name="READ FOR FREE").click()
            await page.wait_for_load_state()
        except TimeoutError:
            self.logger.error("Failed to find cookies management")
