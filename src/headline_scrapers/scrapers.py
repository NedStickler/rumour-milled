from os import PathLike
from headline_scrapers.base import BaseScraper
from playwright.sync_api import TimeoutError


class YahooScraper(BaseScraper):
    def __init__(
        self,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_pages: int = 500,
        save_path: PathLike = ".",
        save_checkpoint: int | None = None,
        headless: bool = True,
    ) -> None:
        super().__init__(
            "https://news.yahoo.com",
            locator_strings,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    def deal_with_cookies(self) -> None:
        self.page.locator("button", has_text="reject").click()
        self.page.wait_for_event("load")


class SkyScraper(BaseScraper):
    def __init__(
        self,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_pages: int = 500,
        save_path: PathLike = ".",
        save_checkpoint: int | None = 10,
        headless: bool = True,
    ) -> None:
        super().__init__(
            "https://news.sky.com",
            locator_strings,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )


class CBCScraper(BaseScraper):
    def __init__(
        self,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_pages: int = 500,
        save_path: PathLike = ".",
        save_checkpoint: int | None = 10,
        headless: bool = True,
    ) -> None:
        super().__init__(
            "https://www.cbc.ca",
            locator_strings,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )

    def deal_with_cookies(self) -> None:
        try:
            self.page.locator("button", has_text="manage").click()
            self.page.wait_for_load_state("load")
            self.page.get_by_role("button", name="Confirm choices").click()
            self.page.wait_for_load_state("load")
        except TimeoutError:
            print("Failed to find cookies management")


class ABCScraper(BaseScraper):
    def __init__(
        self,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_pages: int = 500,
        save_path: PathLike = ".",
        save_checkpoint: int | None = 10,
        headless: bool = True,
    ) -> None:
        super().__init__(
            "https://www.abc.net.au",
            locator_strings,
            ignore_robots_txt,
            max_pages,
            save_path,
            save_checkpoint,
            headless,
        )
