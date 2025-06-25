from pathlib import Path
from scrapy.http import HtmlResponse
from playwright.async_api import async_playwright
import scrapy
import asyncio


class YahooScraper(scrapy.Spider):
    name = "yahoo"

    def start_requests(self):
        url = "https://finance.yahoo.com/"
        html = asyncio.run(self.accept_cookies(url))
        yield HtmlResponse(url=url, body=html, ecoding="utf-8")

    async def accept_cookies(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.click("button.reject-all")
            content = await page.content()
            await browser.close()
            return content

    def parse(self, response):
        yield {"url": response.url, "title": response.css("title::text").get()}
