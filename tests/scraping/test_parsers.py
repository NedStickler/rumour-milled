import pytest
from rumour_milled.scraping.parsers import HtmlParser


@pytest.fixture
def test_html():
    with open("tests/scraping/test.html", "r") as f:
        yield f.read()


def test_parse_hrefs(test_html):
    parser = HtmlParser(test_html)
    hrefs = [
        "https://example.com/test1",
        "https://example.com/test2"
    ]
    assert parser.parse_hrefs() == hrefs


def test_parse_headlines_exact(test_html):
    parser = HtmlParser(test_html)
    headlines = [
        f"Test Headline {i+1}"
        for i in range(3)
    ]
    attrs = {"class": "headline"}
    assert parser.parse_headlines(attr_searches=attrs, exact_match=True) == headlines


def test_parse_headlines_fuzzy(test_html):
    parser = HtmlParser(test_html)
    headlines = [
        f"Test Headline {i+1}"
        for i in range(6)
    ]
    attrs = {"class": "headline"}
    assert parser.parse_headlines(attr_searches=attrs) == headlines