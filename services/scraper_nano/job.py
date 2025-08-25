from rumour_milled.scraping.scrapers import *
from datetime import datetime
from pathlib import Path


if __name__ == "__main__":
    datetime_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_path = Path(f"data/raw/headlines/scraped/{datetime_now}")
    log_path.mkdir(parents=True, exist_ok=True)
    log_path = str(log_path) + "/scrapers.log"
    configs_folder_path = "configs/scraping"

    yahoo_scraper = YahooScraper(
        log_path=log_path,
        max_pages=10,
        config_path=configs_folder_path + "/yahoo.yaml",
    )

    yahoo_scraper.run()