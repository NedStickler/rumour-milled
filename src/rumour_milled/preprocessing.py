import nltk
import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import Optional


def tokenise_headlines(headlines: list[str], model: str = "bert-base-uncased") -> dict:
    """Tokenise raw text headlines.

    Args:
        headlines (list[str]): Raw headlines to be tokenised
        model (str, optional): Model to use for tokenisation. Defaults to "bert-base-uncased".

    Returns:
        dict: _description_
    """
    tokeniser = AutoTokenizer.from_pretrained(model)
    tokens = tokeniser(headlines, padding=True, truncation=True, return_tensors="pt")
    return tokens


def vectorise_tokens(
    tokens: dict,
    model: str = "bert-base-uncased",
    batch_size: Optional[int] = None,
) -> torch.Tensor:
    """Vectorise tokenised headlines.

    Args:
        tokens (dict): Tokenised headlines to be vectorised.
        model (str, optional): Model to use for vectorisation. Defaults to "bert-base-uncased".
        batch_size (Optional[int], optional): Batch size for vectorisation to avoid GPU memory issues. Defaults to None.

    Returns:
        torch.Tensor: Processed headlines as a len(headlines) x 768 tensor.
    """
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
) -> torch.Tensor:
    """Tokenise and then vectorise headlines in order.

    Args:
        headlines (list[str]): Raw headlines to be processed.
        model (str, optional): Model to use for tokenisation and vectorisation. Defaults to "bert-base-uncased".
        batch_size (Optional[int], optional): Batch size for vectorisation to avoid GPU memory issues. Defaults to None.

    Returns:
        torch.Tensor: Processed headlines as a len(headlines) x 768 tensor.
    """
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
