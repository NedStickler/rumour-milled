from headline_scrapers.yahoo import YahooScraper


if __name__ == "__main__":
    yahoo_scraper = YahooScraper(
        root="https://news.yahoo.com/",
        locator_strings=[
            '[data-test-locator="headline"]',
            '[data-test-locator="item-title"]',
            '[data-test-locator="stream-item-title"]',
            '[class*="headline"]',
        ],
        max_pages=100,
        save_path="data/raw/scraped_yahoo_headlines.json",
    )
    yahoo_scraper.start()
