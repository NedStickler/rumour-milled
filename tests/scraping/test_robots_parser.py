import pytest
from rumour_milled.scraping.parsers import RobotsTxtParser


@pytest.fixture
def robots_txt_parser():
    rp = RobotsTxtParser("https://news.yahoo.com/robots.txt")
    rp.read()
    yield rp


def test_denies(robots_txt_parser):
    assert robots_txt_parser.can_fetch("*", "https://news.yahoo.com/nel_ms") == False
    assert robots_txt_parser.can_fetch("*", "/nel_ms") == False
    assert robots_txt_parser.can_fetch("*", "/caas/") == False
    assert robots_txt_parser.can_fetch("*", "/caas/test") == False
    assert robots_txt_parser.can_fetch("Scrapy", "/") == False


def test_allows(robots_txt_parser):
    assert robots_txt_parser.can_fetch("*", "/test") == True
    assert robots_txt_parser.can_fetch("*", "https://news.yahoo.com/test") == True
    assert robots_txt_parser.can_fetch("rumour-milled", "/test") == True
