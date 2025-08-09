from rumour_milled.ml.models.simple import SimpleHeadlineClassifier
from rumour_milled.ml.load import load_headlines
from rumour_milled.ml.preprocess import tokenise_and_vectorise
from rumour_milled.ml.train import Trainer
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
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
    X = tokenise_and_vectorise(headlines_subset, batch_size=128)
    n = X.shape[0] / 2
    y = torch.cat([torch.zeros((n, 1)), torch.ones((n, 1))])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y.squeeze().numpy()
    )
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=True)

    model = SimpleHeadlineClassifier(768, 256, 1)
    loss_fn = nn.BCEWithLogitsLoss()
    optimiser = optim.Adam(model.parameters(), lr=0.001)
    trainer = Trainer(model=model, loss_fn=loss_fn, optimiser=optimiser)
    trainer.train(train_loader=train_loader, validation_loader=val_loader, epochs=1000)
