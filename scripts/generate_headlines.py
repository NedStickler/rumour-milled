from headlines_generators.generators import HeadlinesGenerator
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    hs = HeadlinesGenerator()
    n = 17_257

    hs.generate_headlines(2000)
