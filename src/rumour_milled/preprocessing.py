import nltk
import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import Optional


def tokenise_headlines(
    headlines: list[str], model: str = "bert-base-uncased"
) -> list[dict]:
    tokeniser = AutoTokenizer.from_pretrained(model)
    tokens = tokeniser(headlines, padding=True, truncation=True, return_tensors="pt")
    return tokens


def vectorise_tokens(
    tokens: list[dict],
    model: str = "bert-base-uncased",
    batch_size: Optional[int] = None,
) -> torch.Tensor:
    inputs_len = len(tokens["input_ids"])
    if batch_size is None:
        batch_size = inputs_len
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    vectoriser = AutoModel.from_pretrained(model).to(device)
    vectors = []

    with torch.no_grad():
        for i in range(0, inputs_len, batch_size):
            if i + batch_size > inputs_len:
                batch_size = inputs_len - i
            print(f"Vectorising {i+batch_size}/{inputs_len}")
            batch_tokens = {
                k: v[i : i + batch_size].to(device) for k, v in tokens.items()
            }
            vector = vectoriser(**batch_tokens)
            vectors.append(vector.last_hidden_state[:, 0, :])
    return torch.cat(vectors, dim=0)


def tokenise_and_vectorise(
    headlines: list[str],
    model: str = "bert-base-uncased",
    batch_size: Optional[int] = None,
):
    tokens = tokenise_headlines(headlines, model)
    X = vectorise_tokens(tokens, model, batch_size)
    return X


def nltk_downloads() -> None:
    """Download necessary NLTK packages."""
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")


def preprocess(text: str) -> str:
    """Pre-process text for vectorisation and embedding.

    Args:
        text (str): Text to be cleaned.

    Returns:
        str: Cleaned text.
    """
    text = text.lower()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    cleaned = [
        lemmatizer.lemmatize(word)
        for word in tokens
        if word.isalpha() and word not in stop_words
    ]
    return " ".join(cleaned)


def apply_preprocess(x):
    return x.apply(preprocess)
