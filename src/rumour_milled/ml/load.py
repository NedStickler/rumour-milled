import joblib
import pandas as pd
from typing import Literal
from rumour_milled.storage.dynamodb import HeadlineStorage


def load_external_data(
    label: Literal["combined", "true", "fake"] = "combined"
) -> pd.DataFrame:
    true = pd.read_csv("data/raw/True.csv")
    fake = pd.read_csv("data/raw/Fake.csv")
    true["fake_news"] = 0.0
    fake["fake_news"] = 1.0
    if label == "combined":
        return pd.concat([true, fake])
    if label == "true":
        return true
    if label == "fake":
        return fake


def load_headlines() -> tuple[list[str], list[int]]:
    hs = HeadlineStorage()
    items = hs.get_items()
    headlines = []
    labels = []
    for headline, label in items:
        headlines.append(headline)
        labels.append(int(label))
    return headlines, labels


def load_model(
    model: Literal[
        "logisticregression",
        "randomforestclassifier",
        "gradientboostingclassifier",
        "xgbclassifier",
    ] = "logisticregression",
    embedding: Literal[
        "tfidfvectorizer", "sentencetransformervectoriser"
    ] = "tfidfvectorizer",
):
    return joblib.load(f"models/{model}_{embedding}.pkl")
