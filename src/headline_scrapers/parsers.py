import requests
from urllib.robotparser import RobotFileParser


class RobotsTxtParser(RobotFileParser):
    def __init__(self, url: str = ""):
        super().__init__(url)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def read(self) -> str:
        res = requests.get(self.url, headers=self.headers)
        if res.status_code in (401, 403):
            self.disallow_all = True
        elif res.status_code >= 400 and res.status_code < 500:
            self.allow_all = True
        self.parse(res.text.splitlines())
