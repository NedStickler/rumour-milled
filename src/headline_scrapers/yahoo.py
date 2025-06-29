from os import PathLike
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
