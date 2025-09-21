import pytest
import boto3
from moto import mock_aws
from rumour_milled.storage.dynamodb import HeadlineStorage
from boto3.dynamodb.conditions import Attr


@pytest.fixture
def headline_store():
    with mock_aws():
        yield HeadlineStorage()


def _create_n_headlines(n) -> list[dict]:
    headlines = [
        {"headline": f"test{i}", "label": i}
        for i in range(n)
    ]
    return headlines


def test_put_item(headline_store):
    headline = {"headline": "Test Headline", "label": 1}
    headline_store.put_item(headline)
    items = headline_store.table.get_item(
        Key=headline
    )
    assert items.get("Item") == headline


def test_put_items(headline_store):
    headlines = _create_n_headlines(3)
    headline_store.put_items(headlines)
    items = headline_store.table.scan()
    assert items.get("Items") == headlines


def test_create_table(headline_store):
    headline_store.create_table("test")
    assert headline_store._table_exists("test")


def test_parse_and_append(headline_store):
    items = [
        {"headline": "test1", "label": 0},
        {"headline": "test2", "label": 1},
    ]
    lst = []
    headline_store._HeadlineStorage__parse_and_append(lst, items)
    assert lst == [("test1", 0), ("test2", 1)]


def test_get_all_items(headline_store):
    headlines = _create_n_headlines(10)
    headline_store.put_items(headlines)
    items = headline_store.get_all_items()
    lst = []
    for headline in headlines:
        lst.append((headline["headline"], headline["label"]))
    assert items == lst


def test_get_filtered_items(headline_store):
    items = _create_n_headlines(5)
    target = {"headline": "target", "label": 0}
    items.append(target)
    headline_store.put_items(items)
    hits = headline_store.get_filtered_items(
        filter_expression=Attr("headline").eq("target"),
        max_items=6
    )
    assert hits == [("target", 0)]