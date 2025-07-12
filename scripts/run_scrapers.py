from headline_scrapers.scrapers import *


if __name__ == "__main__":
    yahoo_scraper = YahooScraper(save_path="data/raw/scraped_yahoo_headlines.json")
    sky_scraper = SkyScraper(save_path="data/raw/scraped_sky_headlines.json")
    cbc_scraper = CBCScraper(save_path="data/raw/scraped_cbc_headlines.json")
    abc_scraper = ABCScraper(save_path="data/raw/scraped_abc_headlines.json")
    fox_scraper = FoxScraper(save_path="data/raw/scraped_fox_headlines.json")
    nbc_scraper = NBCScraper(save_path="data/raw/scraped_nbc_headlines.json")
    irish_times_scraper = IrishTimesScraper(
        save_path="data/raw/scraped_irish_times_headlines.json"
    )
    businesstech_scraper = BusinessTechScraper(
        save_path="data/raw/scraped_business_tech_headlines.json"
    )
    rnz_scraper = RNZScraper(save_path="data/raw/scraped_rnz_headlines.json")

    herald_scraper = HeraldScraper(
        save_path="data/raw/scraped_herald_headlines.json",
    )

    scrapers = [
        ("Yahoo", yahoo_scraper),
        ("Sky", sky_scraper),
        ("CBC", cbc_scraper),
        ("ABC", abc_scraper),
        ("Fox", fox_scraper),
        ("NBC", nbc_scraper),
        ("Irish Times", irish_times_scraper),
        ("BusinessTech", businesstech_scraper),
        ("RNZ", rnz_scraper),
        ("Scotsman", herald_scraper),
    ]

    for name, obj in scrapers:
        obj.start()
