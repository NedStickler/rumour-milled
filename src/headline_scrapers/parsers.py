import aiohttp
import asyncio
import aiohttp.test_utils
import requests
from typing import Optional
from urllib.robotparser import RobotFileParser


class RobotsTxtParser(RobotFileParser):
    def __init__(self, url: str = ""):
        super().__init__(url)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    # def read(self):
    #     """Reads the robots.txt URL and feeds it to the parser."""
    #     try:
    #         f = urllib.request.urlopen(self.url)
    #     except urllib.error.HTTPError as err:
    #         if err.code in (401, 403):
    #             self.disallow_all = True
    #         elif err.code >= 400 and err.code < 500:
    #             self.allow_all = True
    #         err.close()
    #     else:
    #         raw = f.read()
    #         self.parse(raw.decode("utf-8").splitlines())

    def read(self) -> str:
        res = requests.get(self.url, headers=self.headers)
        if res.status_code in (401, 403):
            self.disallow_all = True
        elif res.status_code >= 400 and res.status_code < 500:
            self.allow_all = True
        return res.text.splitlines()


if __name__ == "__main__":
    # url = "https://www.cbc.ca/robots.txt"
    # parser = RobotsTxtParser(url)
    # parser.read()
    # print(parser.modified())

    rp = RobotsTxtParser()
    rp.set_url("https://www.cbc.ca/robots.txt")
    rp.read()
    print(rp.can_fetch("*", "/hello"))
