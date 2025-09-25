import pytest
from rumour_milled.scraping.base import BaseScraper


class FakeRobots:
    def __init__(self, allow=True):
        self._allow = allow

    def can_fetch(self, agent, url):
        return self._allow

    def read(self):
        pass


@pytest.mark.parametrize(
    "root,url,expected",
    [
        ("https://example.com", "/test", "https://example.com/test"),
        ("https://example.com", "https://example.com/test", "https://example.com/test"),
        ("https://example.com", "./test/another", "https://example.com/test/another"),
        ("https://example.com/test", "../another", "https://example.com/another"),
        (
            "https://example.com/test",
            "?query=test-query#fragment",
            "https://example.com/test?query=test-query#fragment",
        ),
    ],
)
def test_url_normalisation(monkeypatch, tmp_path, root, url, expected):
    def fake_setup(_self, robots_txt_url=None):
        return FakeRobots(allow=True)

    monkeypatch.setattr(BaseScraper, "setup_robots_txt_parser", fake_setup)

    scraper = BaseScraper(
        root=root,
        attrs={"class": "headline"},
        ignore_robots_txt=False,
        max_workers=1,
        save_path=tmp_path / "out.json",
        log_path=tmp_path / "scraper.log",
    )
    normalised_url = scraper.normalise_url(url)
    assert normalised_url == expected
