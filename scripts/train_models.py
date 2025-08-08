from rumour_milled.ml.models.gan import HeadlinesGenerator, HeadlinesDiscriminator
from rumour_milled.ml.load import load_headlines
from rumour_milled.ml.preprocess import tokenise_and_vectorise
import torch
from sklearn.model_selection import train_test_split
from boto3.dynamodb.conditions import Attr


if __name__ == "__main__":
    real_headlines, _ = load_headlines(
        filter_expression=Attr("label").eq(0), max_items=256
    )
    fake_headlines, _ = load_headlines(
        filter_expression=Attr("label").eq(1), max_items=256
    )

    headlines_subset = real_headlines + fake_headlines
    ones = torch.ones((256, 1))
    zeroes = torch.zeros((256, 1))
    X = tokenise_and_vectorise(headlines_subset, batch_size=128)
    y = torch.cat([torch.zeros((256, 1)), torch.ones((256, 1))])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=True
    )
