from headline_scrapers.scrapers import *
from datetime import datetime
from pathlib import Path


if __name__ == "__main__":
    datetime_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_path = Path(f"data/raw/headlines/scraped/{datetime_now}")
    log_path.mkdir(parents=True, exist_ok=True)
    log_path = str(log_path) + "/scrapers.log"
    configs_folder_path = "src/headline_scrapers/configs"

    yahoo_scraper = YahooScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/yahoo.yaml",
        max_pages=100,
    )
    sky_scraper = SkyScraper(
        log_path=log_path, config_path=configs_folder_path + "/sky.yaml", max_pages=100
    )
    cbc_scraper = CBCScraper(
        log_path=log_path, config_path=configs_folder_path + "/cbc.yaml", max_pages=100
    )
    abc_scraper = ABCScraper(
        log_path=log_path, config_path=configs_folder_path + "/abc.yaml", max_pages=100
    )
    fox_scraper = FoxScraper(
        log_path=log_path, config_path=configs_folder_path + "/fox.yaml", max_pages=100
    )
    nbc_scraper = NBCScraper(
        log_path=log_path, config_path=configs_folder_path + "/nbc.yaml", max_pages=100
    )
    irish_times_scraper = IrishTimesScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/irish-times.yaml",
        max_pages=100,
    )
    businesstech_scraper = BusinessTechScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/businesstech.yaml",
        max_pages=100,
    )
    rnz_scraper = RNZScraper(
        log_path=log_path, config_path=configs_folder_path + "/rnz.yaml", max_pages=100
    )
    herald_scraper = HeraldScraper(
        log_path=log_path,
        config_path=configs_folder_path + "/herald.yaml",
        max_pages=100,
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
