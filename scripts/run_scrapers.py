from headline_scrapers.scrapers import *
from datetime import datetime
from pathlib import Path


if __name__ == "__main__":
    datetime_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    folder_path = Path(f"data/raw/headlines/scraped/{datetime_now}")
    folder_path.mkdir(parents=True, exist_ok=True)
    folder_path = str(folder_path)

    yahoo_scraper = YahooScraper(
        save_path=folder_path + "/scraped_yahoo_headlines.json", save_checkpoint=10
    )
    sky_scraper = SkyScraper(save_path=folder_path + "/scraped_sky_headlines.json")
    cbc_scraper = CBCScraper(
        save_path=folder_path + "/scraped_cbc_headlines.json", headless=False
    )
    abc_scraper = ABCScraper(save_path=folder_path + "/scraped_abc_headlines.json")
    fox_scraper = FoxScraper(save_path=folder_path + "/scraped_fox_headlines.json")
    nbc_scraper = NBCScraper(save_path=folder_path + "/scraped_nbc_headlines.json")
    irish_times_scraper = IrishTimesScraper(
        save_path=folder_path + "/scraped_irish_times_headlines.json"
    )
    businesstech_scraper = BusinessTechScraper(
        save_path=folder_path + "/scraped_business_tech_headlines.json"
    )
    rnz_scraper = RNZScraper(save_path=folder_path + "/scraped_rnz_headlines.json")
    herald_scraper = HeraldScraper(
        save_path=folder_path + "/scraped_herald_headlines.json",
    )

    scrapers = [
        ("Yahoo", yahoo_scraper),
        # ("Sky", sky_scraper),
        # ("CBC", cbc_scraper),
        # ("ABC", abc_scraper),
        # ("Fox", fox_scraper),
        # ("NBC", nbc_scraper),
        # ("Irish Times", irish_times_scraper),
        # ("BusinessTech", businesstech_scraper),
        # ("RNZ", rnz_scraper),
        # ("Scotsman", herald_scraper),
    ]

    for name, scraper in scrapers:
        scraper.run()
