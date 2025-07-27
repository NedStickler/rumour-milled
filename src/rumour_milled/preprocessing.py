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
    if batch_size is None:
        batch_size = len(tokens)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    vectoriser = AutoModel.from_pretrained(model).to(device)
    vectors = []
    with torch.no_grad():
        for i in range(0, len(tokens), batch_size):
            print(f"Vectorising batch {i}")
            batch_tokens = tokens[i : i + batch_size].to(device)
            vector = vectoriser(**{k: v.to(device) for k, v in batch_tokens.items()})
            vectors.append(vector.last_hidden_state[:, 0, :])
    return torch.cat(vectors, dim=0)


def tokenise_and_vectorise(
    headlines: list[str],
    model: str = "bert-base-uncased",
    batch_size: Optional[int] = None,
):
    tokens = tokenise_headlines(headlines, model)
    vector = vectorise_tokens(tokens, model, batch_size)
    return vector


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
