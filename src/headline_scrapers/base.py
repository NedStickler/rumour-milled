from playwright.sync_api import sync_playwright
from queue import SimpleQueue
from os import PathLike
from abc import ABC, abstractmethod
import json


class BaseScraper:
    def __init__(
        self,
        root: str,
        locator_strings: list[str],
        ignore_robots_txt: bool = False,
        max_depth: int = 3,
        save_path: PathLike = ".",
    ) -> None:
        self.root = root
        self.locator_strings = locator_strings
        self.ignore_robots_txt = ignore_robots_txt
        self.max_depth = max_depth
        self.save_path = save_path
        self.depth = 0
        self.queue = SimpleQueue()
        self.visited = []
        self.items = []

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError("start method must be overidden by child class")

    @abstractmethod
    def cookies(self) -> None:
        raise NotImplementedError("cookies method must be overidden by child class")

    def save(self) -> None:
        with open(self.save_path, "w") as f:
            json.dump(self.items, f)
