from pathlib import Path
from scrapy.spiders import SitemapSpider
import scrapy
import json


class BBCScraper(scrapy.Spider):
    name = "yahoo"
    start_urls = ["https://finance.yahoo.com/"]

    def __init__(self):
        self.page_counter = 0

    def parse(self, response):
        yield {"url": response.url, "title": response.css("title::text").get()}
