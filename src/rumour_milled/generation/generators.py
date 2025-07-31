import json
import os
import asyncio
import logging
from rumour_milled.utils.utils import clean_headlines
from rumour_milled.storage.dynamodb import HeadlineStorage
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional
from time import perf_counter


# TODO:
# - Allow save toggle
# - Refactor save after every worker


class HeadlinesGenerator:
    """Generates and stores batches of news headlines using OpenAI's GPT API.

    This class manages asynchronous headline generation, batching, concurrency, and storage in DynamoDB.
    """

    def __init__(
        self,
        max_workers: int = 20,
        log_path: os.PathLike = "generator.log",
        api_key: Optional[str] = None,
    ):
        """Initialize the HeadlinesGenerator, OpenAI client, and supporting locks and storage.

        Args:
            max_workers (int): Maximum number of concurrent workers for headline generation. Defaults to 20.
            api_key (Optional[str]): OpenAI API key. If None, loads from environment variable "OPENAI_API_KEY".
        """
        load_dotenv()
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        self.client = AsyncOpenAI(api_key=api_key)
        self.log_path = log_path
        self.max_workers = max_workers

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
        self.logger = self.setup_logger()
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

    def setup_logger(self) -> None:
        """Set up a logger for the scraper, logging to both console and file.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.basicConfig(
            level=logging.INFO,
            encoding="utf-8",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_path, mode="w"),
            ],
        )
        return logging.getLogger(self.__class__.__name__)

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
        try:
            headlines = json.loads(response.output_text).get("headlines", [])
        except json.decoder.JSONDecodeError:
            self.logger.error("Headline batch failed JSON decode")
            headlines = []
        return headlines

    async def __generate_headlines(self, n: int) -> None:
        """Asynchronously generate n headlines using multiple concurrent workers.

        Args:
            n (int): Total number of headlines to generate.
        """
        ceil_div = lambda a, b: -(a // -b)
        workers = min(self.max_workers, ceil_div(n, 25))
        self._remaining = n
        self.logger.info(f"Starting {workers} workers")

        async def worker():
            while True:
                async with self._remaining_lock:
                    if self._remaining <= 0:
                        return
                    self.logger.info(f"{self._remaining} headlines remaining")
                    batch_size = min(self._remaining, 25)
                    self._remaining -= batch_size

                headlines = await self.generate_headlines_batch(batch_size)

                async with self._headlines_lock:
                    self._headlines.update(headlines)
                    if len(self._headlines) >= n:
                        return
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
        self.logger.info("Saving generated headlines")
        self.headline_storage.put_items(items)

    def generate_headlines(self, n: int) -> None:
        """Synchronous entry point to generate n headlines and save them to storage.

        Args:
            n (int): Total number of headlines to generate.
        """
        start_time = perf_counter()
        asyncio.run(self.__generate_headlines(n))
        self.logger.info(
            f"Generated {len(self._headlines)} headlines in {perf_counter() - start_time:.2f} seconds."
        )
