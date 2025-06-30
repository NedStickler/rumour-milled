from headline_scrapers.scrapers import YahooScraper, SkyScraper, CBCScraper, ABCScraper


if __name__ == "__main__":
    yahoo_scraper = YahooScraper(
        locator_strings=[
            '[data-test-locator="headline"]',
            '[data-test-locator="item-title"]',
            '[data-test-locator="stream-item-title"]',
            '[class*="headline"]',
        ],
        save_path="data/raw/scraped_yahoo_headlines.json",
        max_pages=100,
        save_checkpoint=10,
    )

    sky_scraper = SkyScraper(
        locator_strings=['[class*="headline"]'],
        save_path="data/raw/scraped_sky_headlines.json",
        max_pages=100,
        save_checkpoint=10,
    )

    cbc_scraper = CBCScraper(
        locator_strings=['[class*="headline"]'],
        save_path="data/raw/scraped_cbc_headlines.json",
        max_pages=100,
        save_checkpoint=10,
        headless=False,
    )

    abc_scraper = ABCScraper(
        locator_strings=['[data-component*="CardHeading"]'],
        save_path="data/raw/scraped_abc_headlines.json",
        max_pages=100,
        save_checkpoint=10,
    )

    yahoo_scraper.start()
    sky_scraper.start()
    cbc_scraper.start()
    abc_scraper.start()
