import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Headlines(BaseModel):
    headlines: list[str]


if __name__ == "__main__":
    client = OpenAI()
    instructions = """
    All responses must contain results resembling real news headlines.
    There must be an equal distribution of topics throughout the news headlines.
    You can reference current affairs in the headline.
    """
    response = client.responses.parse(
        model="gpt-4.1",
        instructions=instructions,
        input="Generate 100 fake news headlines.",
        text_format=Headlines,
    )
    headlines = response.output_parsed.headlines
    with open("data/raw/headlines/generated/sample_headlines.json", "w") as f:
        json.dump(headlines, f)
