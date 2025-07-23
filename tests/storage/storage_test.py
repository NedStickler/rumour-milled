from headlines_generators.generators import HeadlinesGenerator
from storage.storage import HeadlineStorage


if __name__ == "__main__":
    hs = HeadlineStorage()
    print(len(hs.get_items()))

    hg = HeadlinesGenerator()
    hg.generate_headlines(9)

    print(len(hs.get_items()))
