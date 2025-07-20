import json
import os
import warnings
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional


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

    async def generate_headlines_batch(self, batch_size: int = 25) -> list[str]:
        response = await self.client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "developer", "content": self.system_prompt},
                {"role": "user", "content": str(batch_size)},
            ],
        )
        return json.loads(response.output_text)

    async def generate_headlines(n: int = 100) -> list[str]:
        return


if __name__ == "__main__":
    hg = HeadlinesGenerator()
    headlines = asyncio.run(hg.generate_headlines_batch())
    print(len(headlines.get("headlines")))
    print(headlines)
