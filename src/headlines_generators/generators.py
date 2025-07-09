import json
import os
import warnings
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional


class HeadlinesGenerator:
    """Generates news headlines using an OpenAI language model.

    This class provides an interface to generate a specified number of realistic news headlines using the OpenAI API.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """Initialize the HeadlinesGenerator.

        Args:
            client (Optional[OpenAI], optional): An OpenAI client instance. If None, loads API key from environment and creates a new client.
        """
        if client is None:
            load_dotenv()
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.client = client
        self.system_prompt = (
            "You are a news headline generator. Your task is to generate realistic news headlines based on the number provided by the user. "
            + "All responses must contain results resembling real news headlines. "
            + "The user will only provide a number, which indicates how many headlines to generate. Generate that many headlines, no more, no less. "
            + "You can reference current affairs in the headlines. "
            + "The headlines must be in English. "
            + "The headlines must be concise, no more than 15 words each. "
            + "Only generate headlines, do not generate any other text or explanations. "
            + "Your output should be formatted as a JSON object with a single key 'headlines'. "
            + "The value should be a list of strings, each string being a headline."
        )

    def generate_headlines(self, num_headlines: int) -> list[str]:
        """Generate a specified number of news headlines.

        Args:
            num_headlines (int): The number of headlines to generate (recommended: 30 or fewer).

        Returns:
            list[str]: A list of generated news headline strings.
        """
        if num_headlines > 30:
            warnings.warn(
                "Generating more than 30 headlines results in inconsistent headline counts, consider reducing the number of headlines to 30 or fewer."
            )
        response = self.client.responses.create(
            model="gpt-4.1",
            input=[
                {"role": "developer", "content": self.system_prompt},
                {"role": "user", "content": str(num_headlines)},
            ],
        )
        return json.loads(response.output_text)
