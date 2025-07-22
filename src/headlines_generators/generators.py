import json
import os
import asyncio
from headline_scrapers.utils import clean_headlines
from storage.storage import HeadlineStorage
from openai import AsyncOpenAI
from dotenv import load_dotenv
from time import perf_counter


class HeadlinesGenerator:
    def __init__(self):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.system_prompt = (
            "You are a news headline generator. Your task is to generate realistic news headlines based on the number provided by the user. "
            + "All responses must contain results resembling real news headlines. "
            + "The user will only provide a number, which indicates how many headlines to generate. Generate that many headlines, no more, no less. "
            + "You can reference current affairs in the headlines. "
            + "The headline must not have truth to them. "
            + "The headlines must be in English. "
            + "The headlines must be concise, no more than 15 words each. "
            + "Your output should be formatted as a JSON object with a single key 'headlines'. "
            + "The value should be a list of strings, each string being a headline."
        )
        self._headlines = set()
        self._remaining = None
        self.max_workers = 20

        self.headline_storage = HeadlineStorage()
        self._headlines_lock = asyncio.Lock()
        self._remaining_lock = asyncio.Lock()

    @property
    def headlines(self):
        return self._headlines

    async def generate_headlines_batch(self, batch_size: int = 25) -> list[str]:
        response = await self.client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "developer", "content": self.system_prompt},
                {"role": "user", "content": str(batch_size)},
            ],
        )
        return json.loads(response.output_text).get("headlines", [])

    async def __generate_headlines(self, n: int) -> None:
        ceil_div = lambda a, b: -(a // -b)
        workers = min(self.max_workers, ceil_div(n, 25))
        self._remaining = n

        async def worker():
            print("Worker generating headlines!")
            while True:
                async with self._remaining_lock:
                    if self._remaining <= 0:
                        break
                    batch_size = min(self._remaining, 25)
                    self._remaining -= batch_size

                headlines = await self.generate_headlines_batch(batch_size)

                async with self._headlines_lock:
                    self._headlines.update(headlines)
                    if len(self._headlines) >= n:
                        break
                self.save()
                await asyncio.sleep(0.5)

        async with asyncio.TaskGroup() as tg:
            for _ in range(workers):
                tg.create_task(worker())

    def save(self):
        items = [
            {"headline": headline, "label": 1}
            for headline in clean_headlines(self._headlines)
        ]
        self.headline_storage.put_items(items)

    def generate_headlines(self, n: int) -> None:
        asyncio.run(self.__generate_headlines(n))
        self.save()


if __name__ == "__main__":
    hg = HeadlinesGenerator()
    start = perf_counter()
    hg.generate_headlines(100)
    print(len(hg.headlines))
    print(f"Done in {perf_counter() - start:.2f} seconds")
