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
    # import rumour_milled.scraping.base as base_mod
    # monkeypatch.setattr(base_mod, "validate_url", lambda x: True)
    # monkeypatch.setattr(asyncio, "sleep", lambda x: asyncio.sleep(0))
    return s


@pytest.mark.asyncio
async def test_scrape_page(monkeypatch, scraper):
    recorder = {"goto_calls": []}
    page = FakePage(recorder)
    elements = ["Test Headline 1", "Test Headline 2"]
    hrefs = ["/rel", "https://example.com/test1", "/rel"]

    class FakeHtmlParser:
        def __init__(self, html):
            self._html = html

        def parse_text(self, attrs):
            assert attrs == scraper.attrs
            return elements

        def parse_hrefs(self):
            return hrefs

    monkeypatch.setattr("rumour_milled.scraping.base.HtmlParser", FakeHtmlParser)

    assert len(scraper.items) == 0
    assert scraper.queue.qsize() == 0

    await scraper.scrape_page("https://example.com/root", page)
    assert recorder["goto_calls"] == ["https://example.com/root"]

    async with scraper.visited_lock:
        assert "https://example.com/root" in scraper.visited

    assert scraper.items == elements
    assert scraper.queue.qsize() == 2
    href1 = await scraper.queue.get()
    href2 = await scraper.queue.get()
    assert [href1, href2] == ["/rel", "https://example.com/test1"]


@pytest.mark.asyncio
async def test_respects_normalised_seen(monkeypatch, scraper):
    recorder = {"goto_calls": []}
    page = FakePage(recorder)
    hrefs = ["/rel", "/other"]

    class FakeHtmlParser:
        def __init__(self, html):
            self._html = html

        def parse_text(self, attrs):
            return []

        def parse_hrefs(self):
            return hrefs

    monkeypatch.setattr("rumour_milled.scraping.base.HtmlParser", FakeHtmlParser)
    normalised_rel = scraper.normalise_url("/rel")
    async with scraper.seen_lock:
        scraper.seen.add(normalised_rel)
    await scraper.scrape_page("https://example.com/test1", page)

    assert scraper.queue.qsize() == 1
    assert await scraper.queue.get() == "/other"


@pytest.mark.asyncio
async def test_scrape_empty_page(monkeypatch, scraper):
    recorder = {"goto_calls": []}
    page = FakePage(recorder)

    class FakeHtmlParser:
        def __init__(self, html):
            self._html = html

        def parse_text(self, attrs):
            return []

        def parse_hrefs(self):
            return []

    monkeypatch.setattr("rumour_milled.scraping.base.HtmlParser", FakeHtmlParser)
    await scraper.scrape_page("https://example.com/test1", page)
    async with scraper.visited_lock:
        assert "https://example.com/test1" in scraper.visited
    assert scraper.queue.qsize() == 0
    assert scraper.items == []


@pytest.mark.asyncio
async def test_failure_propagation(monkeypatch, scraper):
    recorder = {"goto_calls": []}
    page = FakePage(recorder)

    class Bang(Exception):
        pass

    class FakeHtmlParser:
        def __init__(self, html):
            self._html = html

        def parse_text(self, attrs):
            raise Bang("Bang")

        def parse_hrefs(self):
            []

    monkeypatch.setattr("rumour_milled.scraping.base.HtmlParser", FakeHtmlParser)

    with pytest.raises(Exception):
        await scraper.scrape_page("https://example.com/test1", page)

    async with scraper.visited_lock:
        assert "https://example.com/test1" in scraper.visited
    assert scraper.queue.qsize() == 0
    assert scraper.items == []
