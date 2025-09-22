import requests
import re
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup


class RobotsTxtParser(RobotFileParser):
    """Custom robots.txt parser with user-agent and error handling.

    Args:
        url (str): URL to the robots.txt file.

    Attributes:
        headers (dict): HTTP headers used for requests, including a custom User-Agent.
    """

    def __init__(self, url: str = ""):
        """Initialize the RobotsTxtParser.

        Args:
            url (str): URL to the robots.txt file.
        """
        super().__init__(url)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def read(self) -> str:
        """Read and parse the robots.txt file from the specified URL.

        Returns:
            str: The content of the robots.txt file.
        """
        res = requests.get(self.url, headers=self.headers, timeout=10)
        if res.status_code in (401, 403):
            self.disallow_all = True
        elif res.status_code >= 400 and res.status_code < 500:
            self.allow_all = True
        self.parse(res.text.splitlines())


class HtmlParser:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, "html.parser")

    def parse_hrefs(self):
        return [a.get("href") for a in self.soup.find_all("a")]

    def parse_headlines(self, attrs: dict[str, list], exact_match: bool = False):
        if not exact_match:
            attrs = {k: re.compile(rf"(?i).*{v}.*") for k, v in attrs.items()}

        headlines = []
        for k, v in attrs.items():
            headlines += [
                headline.text for headline in self.soup.find_all(attrs={k: v})
            ]
        return headlines


if __name__ == "__main__":
    with open("tests/scraping/test.html", "r") as f:
        html_content = f.read()
    parser = HtmlParser(html_content)
    attrs = {"test1": "headline", "attr": "headline", "another-attr": "headline"}
    headlines = parser.parse_headlines(attrs)
    print(headlines)
