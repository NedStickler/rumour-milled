import joblib
import pandas as pd
from typing import Literal


def load_data(label: Literal["combined", "true", "fake"] = "combined") -> pd.DataFrame:
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


def load_model(
    model: Literal[
        "logisticregression", "randomforestclassifier"
    ] = "logisticregression",
    embedding: Literal["tfidf"] = "tfidf",
):
    return joblib.load(f"models/{model}_{embedding}.pkl")
