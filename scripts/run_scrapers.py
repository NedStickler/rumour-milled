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
        max_pages=10,
        save_path="data/raw/scraped_yahoo_headlines.json",
        save_checkpoint=5,
    )
    yahoo_scraper.start()
