from playwright.sync_api import sync_playwright
from queue import SimpleQueue


class BaseScraper:
    def __init__(
        self, root: str, ignore_robots_txt: bool = False, max_depth: int = 3
    ) -> None:
        self.root = root
        self.ignore_robots_txt = ignore_robots_txt
        self.max_depth = max_depth
        self.depth = 0
        self.queue = SimpleQueue()
        self.visited = []
        self.items = []

    def start() -> None:
        return

    def save() -> None:
        return
