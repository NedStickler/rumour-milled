from headline_scrapers.scrapers import *


if __name__ == "__main__":
    yahoo_scraper = YahooScraper(
        locator_strings=[
            '[data-test-locator="headline"]',
            '[data-test-locator="item-title"]',
            '[data-test-locator="stream-item-title"]',
            '[class*="headline"]',
        ],
        save_path="data/raw/scraped_yahoo_headlines.json",
        save_checkpoint=10,
    )

    sky_scraper = SkyScraper(
        locator_strings=['[class*="headline"]'],
        save_path="data/raw/scraped_sky_headlines.json",
        save_checkpoint=10,
    )

    cbc_scraper = CBCScraper(
        locator_strings=['[class*="headline"]'],
        save_path="data/raw/scraped_cbc_headlines.json",
        save_checkpoint=10,
        headless=False,
    )

    abc_scraper = ABCScraper(
        locator_strings=['[data-component*="CardHeading"]'],
        save_path="data/raw/scraped_abc_headlines.json",
        save_checkpoint=10,
    )

    fox_scraper = FoxScraper(
        locator_strings=['[class*="title"]'],
        save_path="data/raw/scraped_fox_headlines.json",
        save_checkpoint=10,
    )

    nbc_scraper = NBCScraper(
        locator_strings=['[class*="headline"]'],
        save_path="data/raw/scraped_nbc_headlines.json",
        save_checkpoint=10,
    )

    irish_times_scraper = IrishTimesScraper(
        locator_strings=['[class*="heading"]'],
        save_path="data/raw/scraped_irish_times_headlines.json",
        save_checkpoint=10,
    )

    scrapers = [
        ("Yahoo", yahoo_scraper),
        ("Sky", sky_scraper),
        ("CBC", cbc_scraper),
        ("ABC", abc_scraper),
        ("Fox", fox_scraper),
        ("NBC", nbc_scraper),
        ("Irish Times", irish_times_scraper),
    ]

    for name, obj in scrapers:
        try:
            obj.start()
        except Exception:
            print(f"{name} scraper failed at page {obj.page_number}")
