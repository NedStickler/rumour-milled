from os import PathLike
from headline_scrapers.base import BaseScraper
from playwright.sync_api import TimeoutError


class YahooScraper(BaseScraper):
    """Scraper for Yahoo News headlines.

    Inherits from BaseScraper and sets the root URL to Yahoo News.
    """

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
        """Initialize YahooScraper with Yahoo News as the root URL."""
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

    def deal_with_cookies(self) -> None:
        """Handle Yahoo's cookie consent dialog by clicking the 'reject' button."""
        self.page.locator("button", has_text="reject").click()
        self.page.wait_for_load_state()


class SkyScraper(BaseScraper):
    """Scraper for Sky News headlines.

    Inherits from BaseScraper and sets the root URL to Sky News.
    """

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
        """Initialize SkyScraper with Sky News as the root URL."""
        super().__init__(
            "https://news.sky.com",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )


class CBCScraper(BaseScraper):
    """Scraper for CBC News headlines.

    Inherits from BaseScraper and sets the root URL to CBC News.
    """

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
        """Initialize CBCScraper with CBC News as the root URL."""
        super().__init__(
            "https://www.cbc.ca",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    def deal_with_cookies(self) -> None:
        """Handle CBC's cookie consent dialog by clicking the appropriate buttons."""
        try:
            self.page.locator("button", has_text="manage").click()
            self.page.wait_for_load_state()
            self.page.get_by_role("button", name="Confirm choices").click()
            self.page.wait_for_load_state()
        except TimeoutError:
            print("Failed to find cookies management")


class ABCScraper(BaseScraper):
    """Scraper for ABC News headlines.

    Inherits from BaseScraper and sets the root URL to ABC News.
    """

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
        """Initialize ABCScraper with ABC News as the root URL."""
        super().__init__(
            "https://www.abc.net.au",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )


class FoxScraper(BaseScraper):
    """Scraper for Fox News headlines.

    Inherits from BaseScraper and sets the root URL to Fox News.
    """

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
        """Initialize FoxScraper with Fox News as the root URL."""
        super().__init__(
            "https://www.foxnews.com",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )


class NBCScraper(BaseScraper):
    """Scraper for NBC News headlines.

    Inherits from BaseScraper and sets the root URL to NBC News.
    """

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
        """Initialize NBCScraper with NBC News as the root URL."""
        super().__init__(
            "https://www.nbcnews.com",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    def deal_with_cookies(self):
        """Handle NBC's cookie consent dialog by clicking the 'Continue' button."""
        self.page.get_by_role("button", name="Continue").click()
        self.page.wait_for_load_state()


class IrishTimesScraper(BaseScraper):
    """Scraper for Irish Times headlines.

    Inherits from BaseScraper and sets the root URL to Irish Times.
    """

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
        """Initialize IrishTimesScraper with Irish Times as the root URL."""
        super().__init__(
            "https://www.irishtimes.com",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    def deal_with_cookies(self):
        """Handle Irish Times' cookie consent dialog by clicking the 'manage' and 'reject' buttons."""
        self.page.get_by_role("button", name="manage").click()
        self.page.wait_for_load_state()
        self.page.get_by_role("button", name="reject").click()
        self.page.wait_for_load_state()


class BusinessTechScraper(BaseScraper):
    """Scraper for BusinessTech headlines.

    Inherits from BaseScraper and sets the root URL to BusinessTech.
    """

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
        """Initialize BusinessTechScraper with BusinessTech as the root URL."""
        super().__init__(
            "https://businesstech.co.za",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )


class RNZScraper(BaseScraper):
    """Scraper for RNZ headlines.

    Inherits from BaseScraper and sets the root URL to RNZ.
    """

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
        """Initialize RNZScraper with RNZ as the root URL."""
        super().__init__(
            "https://www.rnz.co.nz",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )


class HeraldScraper(BaseScraper):
    """Scraper for Herald Scotland headlines.

    Inherits from BaseScraper and sets the root URL to Herald Scotland.
    """

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
        """Initialize HeraldScraper with Herald Scotland as the root URL."""
        super().__init__(
            "https://www.heraldscotland.com",
            locator_strings,
            robots_txt_url,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    def deal_with_cookies(self):
        """Handle Herald Scotland's cookie consent dialog by clicking the 'Reject All' and 'READ FOR FREE' buttons."""
        try:
            self.page.get_by_role("button", name="Reject All").click()
            self.page.wait_for_load_state()
            self.page.get_by_role("button", name="READ FOR FREE").click()
            self.page.wait_for_load_state()
        except TimeoutError:
            print("Failed to find cookies management")
