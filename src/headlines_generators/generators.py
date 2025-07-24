import json
import os
import asyncio
from rumour_milled.utils import clean_headlines
from storage.dynamodb import HeadlineStorage
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional


class HeadlinesGenerator:
    """Generates and stores batches of news headlines using OpenAI's GPT API.

    This class manages asynchronous headline generation, batching, concurrency, and storage in DynamoDB.
    """

    def __init__(self, max_workers: int = 20, api_key: Optional[str] = None):
        """Initialize the HeadlinesGenerator, OpenAI client, and supporting locks and storage.

        Args:
            max_workers (int): Maximum number of concurrent workers for headline generation. Defaults to 20.
            api_key (Optional[str]): OpenAI API key. If None, loads from environment variable "OPENAI_API_KEY".
        """
        load_dotenv()
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        self.client = AsyncOpenAI(api_key=api_key)
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

        self.max_workers = max_workers

        self.headline_storage = HeadlineStorage()
        self._headlines_lock = asyncio.Lock()
        self._remaining_lock = asyncio.Lock()

    @property
    def headlines(self):
        """Get the set of generated headlines.

        Returns:
            set: The set of generated headlines.
        """
        return self._headlines

    async def generate_headlines_batch(self, batch_size: int = 25) -> list[str]:
        """Generate a batch of news headlines using the OpenAI API.

        Args:
            batch_size (int): Number of headlines to generate in this batch.

        Returns:
            list[str]: List of generated headlines.
        """
        response = await self.client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "developer", "content": self.system_prompt},
                {"role": "user", "content": str(batch_size)},
            ],
        )
        return json.loads(response.output_text).get("headlines", [])

    async def __generate_headlines(self, n: int) -> None:
        """Asynchronously generate n headlines using multiple concurrent workers.

        Args:
            n (int): Total number of headlines to generate.
        """
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
                await asyncio.sleep(0.5)
                self.save(headlines)

        async with asyncio.TaskGroup() as tg:
            for _ in range(workers):
                tg.create_task(worker())

    def save(self, headlines: Optional[list[str]] = None):
        """Save the generated headlines to DynamoDB using HeadlineStorage."""
        if headlines is None:
            headlines = self._headlines
        items = [
            {"headline": headline, "label": 1}
            for headline in clean_headlines(headlines)
        ]
        self.headline_storage.put_items(items)

    def generate_headlines(self, n: int) -> None:
        """Synchronous entry point to generate n headlines and save them to storage.

        Args:
            n (int): Total number of headlines to generate.
        """
        asyncio.run(self.__generate_headlines(n))
