from rumour_milled.ml.models.gan import HeadlinesGenerator, HeadlinesDiscriminator
from rumour_milled.ml.load import load_headlines
from rumour_milled.ml.preprocess import tokenise_and_vectorise
import torch
from sklearn.model_selection import train_test_split


if __name__ == "__main__":
    headlines, labels = load_headlines()
    real_headlines = [
        headline for headline, label in zip(headlines, labels) if label == 0
    ]
    fake_headlines = [
        headline for headline, label in zip(headlines, labels) if label == 1
    ]
    headlines_subset = real_headlines[:256] + fake_headlines[:256]
    ones = torch.ones((256, 1))
    zeroes = torch.zeros((256, 1))
    print()
    # X = tokenise_and_vectorise(headlines_subset, batch_size=128)
    # y = torch.zeros_like(X, dtype=torch.float)
