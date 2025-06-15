
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def nltk_downloads() -> None:
    nltk.download("punkt")
    nltk.download("stopwords")
    nltk.download("wordnet")


def preprocess(text: str) -> str:
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


if __name__ == "__main__":
    text = "This is a string! What do you think about this string?"
    preprocessed_text = preprocess(text)
    print(preprocessed_text)