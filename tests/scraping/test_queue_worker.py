import asyncio
import pytest
from rumour_milled.scraping.base import BaseScraper


class FakePage:
    def __init__(self, recorder):
        self.recorder = recorder
        self.closed = False

    async def goto(self, url, wait_until="load"):
        self.recorder["goto_calls"].append(url)

    async def content(self):
        return "<html></html>"

    async def close(self):
        self.closed = True
        self.recorder["close_calls"] += 1


class FakeContext:
    def __init__(self, recorder):
        self.recorder = recorder

    async def new_page(self):
        self.recorder["new_page_calls"] += 1
        return FakePage(self.recorder)

    async def close(self):
        pass


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
        max_workers=1,
    )
    import rumour_milled.scraping.base as base_mod

    monkeypatch.setattr(base_mod, "validate_url", lambda x: True)
    # monkeypatch.setattr(asyncio, "sleep", lambda x: asyncio.sleep(0))
    return s


@pytest.mark.asyncio
async def test_respects_max_pages(scraper, monkeypatch):
    recorder = {"new_page_calls": 0, "goto_calls": [], "close_calls": 0, "scrapes": 0}
    scraper.context = FakeContext(recorder)
    scraper.max_pages = 5

    for i in range(10):
        await scraper.queue.put(f"https://example.com/test{i}")

    async def fake_scrape(url, page):
        recorder["scrapes"] += 1

    monkeypatch.setattr(scraper, "scrape_page", fake_scrape)
    await asyncio.wait_for(scraper.process_queue(), timeout=15)

    assert recorder["scrapes"] == 5
    assert recorder["new_page_calls"] == 5
    assert recorder["close_calls"] == 5


@pytest.mark.asyncio
async def test_queue_hanging(scraper, monkeypatch):
    recorder = {"new_page_calls": 0, "goto_calls": [], "close_calls": 0, "scrapes": 0}
    scraper.context = FakeContext(recorder)
    scraper.max_pages = 5

    await scraper.queue.put(f"https://example.com/test1")

    async def fake_scrape(url, page):
        recorder["scrapes"] += 1

    monkeypatch.setattr(scraper, "scrape_page", fake_scrape)
    await asyncio.wait_for(scraper.process_queue(), timeout=10)


@pytest.mark.asyncio
async def test_save_checkpoint(scraper, monkeypatch):
    recorder = {
        "new_page_calls": 0,
        "goto_calls": [],
        "close_calls": 0,
        "scrapes": 0,
        "saves": 0,
    }
    scraper.context = FakeContext(recorder)
    scraper.max_pages = 5
    scraper.save_checkpoint = 2

    for i in range(5):
        await scraper.queue.put(f"https://example.com/test{i}")

    async def fake_scrape(url, page):
        recorder["scrapes"] += 1

    async def fake_save():
        recorder["saves"] += 1

    monkeypatch.setattr(scraper, "scrape_page", fake_scrape)
    monkeypatch.setattr(scraper, "save", fake_save)
    await asyncio.wait_for(scraper.process_queue(), timeout=10)

    assert recorder["saves"] == 2


@pytest.mark.asyncio
async def test_failures_captured(scraper, monkeypatch):
    recorder = {
        "new_page_calls": 0,
        "goto_calls": [],
        "close_calls": 0,
        "scrapes": 0,
        "saves": 0,
    }
    scraper.context = FakeContext(recorder)
    scraper.max_pages = 2

    class Bang(Exception):
        pass

    async def fake_scrape(url, page):
        raise Bang("Boom")

    monkeypatch.setattr(scraper, "scrape_page", fake_scrape)
    await scraper.queue.put("https://example.com/test1")
    await asyncio.wait_for(scraper.process_queue(), timeout=15)

    assert len(scraper.failures) == 1
    assert isinstance(scraper.failures[0][1], Bang)


@pytest.mark.asyncio
async def test_already_seen(scraper):
    href = "/test1"
    n = 20

    results = await asyncio.gather(*[scraper.already_seen(href) for _ in range(n)])
    assert results.count(False) == 1
    assert results.count(True) == n - 1

    normalised_href = scraper.normalise_url(href)
    async with scraper.seen_lock:
        assert normalised_href in scraper.seen
