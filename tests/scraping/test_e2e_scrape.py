import pytest
import asyncio
from rumour_milled.scraping.base import BaseScraper


class FakePage:
    def __init__(self, recorder):
        self._recorder = recorder

    async def goto(self, url, wait_until="load"):
        self._recorder["goto_calls"].append(url)

    async def close(self):
        self._recorder["page_close_calls"] += 1


class FakeContext:
    def __init__(self, recorder):
        self._recorder = recorder

    async def new_page(self):
        self._recorder["new_page_calls"] += 1
        return FakePage(self._recorder)

    async def close(self):
        self._recorder["context_close_calls"] += 1


class FakeBrowser:
    def __init__(self, recorder):
        self._recorder = recorder

    async def new_context(self, user_agent="user_agent"):
        self._recorder["new_context_calls"] += 1
        return FakeContext(self._recorder)

    async def close(self):
        self._recorder["browser_close_calls"] += 1


class FakeChromium:
    def __init__(self, recorder):
        self._recorder = recorder

    async def launch(self, headless=True):
        self._recorder["chromium_launch_calls"] += 1
        return FakeBrowser(self._recorder)


class FakeAsyncPlayright:
    def __init__(self, recorder):
        self._recorder = recorder
        self.chromium = FakeChromium(self._recorder)

    async def __aenter__(self):
        self._recorder["async_cm_enter_calls"] += 1
        return self

    async def __aexit__(self, *exc):
        self._recorder["async_cm_exit_calls"] += 1
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
    # import rumour_milled.scraping.base as base_mod
    # monkeypatch.setattr(base_mod, "validate_url", lambda x: True)
    # monkeypatch.setattr(asyncio, "sleep", lambda x: asyncio.sleep(0))
    return s


@pytest.mark.asyncio
async def test_e2e_scrape(monkeypatch, scraper):
    recorder = {
        "goto_calls": [],
        "page_close_calls": 0,
        "new_page_calls": 0,
        "context_close_calls": 0,
        "new_context_calls": 0,
        "browser_close_calls": 0,
        "chromium_launch_calls": 0,
        "async_cm_enter_calls": 0,
        "async_cm_exit_calls": 0,
        "process_queue_calls": 0,
        "save_calls": 0,
    }

    async def fake_process_queue():
        recorder["process_queue_calls"] += 1

    async def fake_save():
        recorder["save_calls"] += 1

    monkeypatch.setattr(scraper, "process_queue", fake_process_queue)
    monkeypatch.setattr(scraper, "save", fake_save)
    monkeypatch.setattr(
        "rumour_milled.scraping.base.async_playwright",
        lambda: FakeAsyncPlayright(recorder),
    )

    await asyncio.wait_for(scraper.start(), timeout=15)
    assert recorder["goto_calls"] == ["https://example.com"]
    assert recorder["page_close_calls"] == 1
    assert recorder["new_page_calls"] == 1
    assert recorder["context_close_calls"] == 1
    assert recorder["new_context_calls"] == 1
    assert recorder["browser_close_calls"] == 1
    assert recorder["chromium_launch_calls"] == 1
    assert recorder["async_cm_enter_calls"] == 1
    assert recorder["async_cm_exit_calls"] == 1
    assert recorder["process_queue_calls"] == 1
    assert recorder["save_calls"] == 1
