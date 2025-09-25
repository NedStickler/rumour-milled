import pytest
from rumour_milled.scraping.base import BaseScraper


class FakeRobots:
    def __init__(self, allow=True):
        self._allow = allow

    def can_fetch(self, agent, url):
        return self._allow

    def read(self):
        pass


@pytest.fixture
def scraper(monkeypatch, tmp_path):
    def fake_setup(_self, robots_txt_url=None):
        return FakeRobots(allow=True)

    monkeypatch.setattr(BaseScraper, "setup_robots_txt_parser", fake_setup)

    s = BaseScraper(
        root="https://example.com",
        attrs={"class": "headline"},
        ignore_robots_txt=False,
        save_path=tmp_path / "out.json",
        log_path=tmp_path / "scraper.log",
    )
    return s


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url,is_valid,robots_allow,already_visited,expected",
    [
        ("https://example.com/test1", True, True, True, False),
        ("https://example.com/test2", True, True, False, True),
        ("https://example.com/test3", True, False, True, False),
        ("https://example.com/test4", True, False, False, False),
        ("test5", False, True, True, False),
        ("test6", False, True, False, False),
        ("test7", False, False, True, False),
        ("test7", False, False, False, False),
    ],
)
async def test_can_vist(
    monkeypatch, scraper, url, is_valid, robots_allow, already_visited, expected
):
    import rumour_milled.scraping.base as base_mod

    monkeypatch.setattr(base_mod, "validate_url", lambda x: is_valid)

    scraper.robots_parser = FakeRobots(allow=robots_allow)

    if already_visited:
        async with scraper.visited_lock:
            scraper.visited.add(url)

    can_visit = await scraper.can_visit(url)
    assert can_visit == expected
