import pytest
from rumour_milled.scraping.parsers import HtmlParser


@pytest.fixture
def test_html():
    with open("tests/scraping/test.html", "r") as f:
        yield f.read()


def test_parse_hrefs(test_html):
    parser = HtmlParser(test_html)
    hrefs = [f"https://example.com/test{i}" for i in range(1, 4)]
    assert parser.parse_hrefs() == hrefs


def test_parse_headlines_exact(test_html):
    parser = HtmlParser(test_html)
    headlines = [f"Test Headline {i}" for i in range(1, 4)]
    attrs = {"class": "headline"}
    assert parser.parse_headlines(attrs=attrs, exact_match=True) == headlines


def test_parse_headlines_fuzzy(test_html):
    parser = HtmlParser(test_html)
    headlines = [f"Test Headline {i}" for i in range(1, 7)]
    attrs = {"class": "headline"}
    assert parser.parse_headlines(attrs=attrs) == headlines


def test_parse_attrs(test_html):
    parser = HtmlParser(test_html)
    headlines = [f"Test Headline {i}" for i in range(7, 10)]
    attrs = {"test1": "headline", "attr": "headline", "another-attr": "headline"}
    assert parser.parse_headlines(attrs=attrs) == headlines


def test_nested_headlines(test_html):
    parser = HtmlParser(test_html)
    attrs = {"class": "multiple"}
    assert len(parser.parse_headlines(attrs, exact_match=True)) == 1
