from rumour_milled.scraping.scrapers import *
from datetime import datetime
from pathlib import Path


if __name__ == "__main__":
    datetime_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_path = Path(f"data/raw/headlines/scraped/{datetime_now}")
    log_path.mkdir(parents=True, exist_ok=True)
    log_path = str(log_path) + "/scrapers.log"
    configs_folder_path = "configs"

    yahoo_scraper = YahooScraper(
        log_path=log_path, config_path=configs_folder_path + "/yahoo.yaml"
    )
    sky_scraper = SkyScraper(
        log_path=log_path, config_path=configs_folder_path + "/sky.yaml"
    )
    cbc_scraper = CBCScraper(
        log_path=log_path, config_path=configs_folder_path + "/cbc.yaml"
    )
    abc_scraper = ABCScraper(
        log_path=log_path, config_path=configs_folder_path + "/abc.yaml"
    )
    fox_scraper = FoxScraper(
        log_path=log_path, config_path=configs_folder_path + "/fox.yaml"
    )
    nbc_scraper = NBCScraper(
        log_path=log_path, config_path=configs_folder_path + "/nbc.yaml"
    )
    irish_times_scraper = IrishTimesScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/irish-times.yaml",
    )
    businesstech_scraper = BusinessTechScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/businesstech.yaml",
    )
    rnz_scraper = RNZScraper(
        log_path=log_path, config_path=configs_folder_path + "/rnz.yaml"
    )
    herald_scraper = HeraldScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/herald.yaml",
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
        ("Herald", herald_scraper),
    ]

    for name, scraper in scrapers:
        scraper.run()
