from headlines_generators.generators import HeadlinesGenerator
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime


if __name__ == "__main__":
    load_dotenv()

    datetime_now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_path = Path(f"data/raw/headlines/generated/{datetime_now}")
    log_path.mkdir(parents=True, exist_ok=True)
    log_path = str(log_path) + "/generator.log"

    hs = HeadlinesGenerator(log_path=log_path)
    n = 1_000
    hs.generate_headlines(n)
