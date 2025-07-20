from headline_scrapers.scrapers import *
from datetime import datetime
from pathlib import Path


if __name__ == "__main__":
    datetime_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    save_folder_path = Path(f"data/raw/headlines/scraped/{datetime_now}")
    save_folder_path.mkdir(parents=True, exist_ok=True)
    save_folder_path = str(save_folder_path)
    configs_folder_path = "src/headline_scrapers/configs"

    yahoo_scraper = YahooScraper(
        save_path=save_folder_path + "/scraped_yahoo_headlines.json",
        config_path=configs_folder_path + "/yahoo.yaml",
        max_pages=100,
    )
    sky_scraper = SkyScraper(
        save_path=save_folder_path + "/scraped_sky_headlines.json",
        config_path=configs_folder_path + "/sky.yaml",
    )
    cbc_scraper = CBCScraper(
        save_path=save_folder_path + "/scraped_cbc_headlines.json",
        config_path=configs_folder_path + "/cbc.yaml",
    )
    abc_scraper = ABCScraper(
        save_path=save_folder_path + "/scraped_abc_headlines.json",
        config_path=configs_folder_path + "/abc.yaml",
    )
    fox_scraper = FoxScraper(
        save_path=save_folder_path + "/scraped_fox_headlines.json",
        config_path=configs_folder_path + "/fox.yaml",
    )
    nbc_scraper = NBCScraper(
        save_path=save_folder_path + "/scraped_nbc_headlines.json",
        config_path=configs_folder_path + "/nbc.yaml",
    )
    irish_times_scraper = IrishTimesScraper(
        save_path=save_folder_path + "/scraped_irish_times_headlines.json",
        config_path=configs_folder_path + "/irish-times.yaml",
    )
    businesstech_scraper = BusinessTechScraper(
        save_path=save_folder_path + "/scraped_business_tech_headlines.json",
        config_path=configs_folder_path + "/businesstech.yaml",
    )
    rnz_scraper = RNZScraper(
        save_path=save_folder_path + "/scraped_rnz_headlines.json",
        config_path=configs_folder_path + "/rnz.yaml",
    )
    herald_scraper = HeraldScraper(
        save_path=save_folder_path + "/scraped_herald_headlines.json",
        config_path=configs_folder_path + "/herald.yaml",
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
        # ("Herald", herald_scraper),
    ]

    for name, scraper in scrapers:
        scraper.run()
