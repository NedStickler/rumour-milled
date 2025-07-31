from rumour_milled.ml.models.gan import HeadlinesGenerator, HeadlinesDiscriminator
from rumour_milled.ml.load import load_headlines
from rumour_milled.ml.preprocess import tokenise_and_vectorise
import torch


if __name__ == "__main__":
    headlines, labels = load_headlines()
    real_headlines = [
        headline for headline, label in zip(headlines, labels) if label == 1
    ]
    real_headlines_subset = real_headlines[:512]
    X = tokenise_and_vectorise(real_headlines_subset, batch_size=128)
    y = torch.zeros_like(X, dtype=torch.float).unsqueeze(1)
