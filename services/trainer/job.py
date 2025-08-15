from rumour_milled.ml.models.simple import SimpleHeadlineClassifier
from rumour_milled.ml.train import Trainer
from rumour_milled.ml.load import load_headlines
from rumour_milled.ml.preprocess import tokenise_and_vectorise
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader
import torch
import torch.nn as nn
import torch.optim as optim
import os
import io
import boto3
from boto3.dynamodb.conditions import Attr


# TODO:
# - Change hardcoded model/loss/optimiser


def main(run_id, epochs, lr, batch_size, real_size, fake_size, test_size, random_state):
    real_headlines, _ = load_headlines(
        filter_expression=Attr("label").eq(0), max_items=real_size
    )
    fake_headlines, _ = load_headlines(
        filter_expression=Attr("label").eq(1), max_items=fake_size
    )
    headlines = real_headlines + fake_headlines
    X = tokenise_and_vectorise(headlines, batch_size=128)
    real_y = torch.zeros((real_size, 1))
    fake_y = torch.ones((fake_size, 1))
    y = torch.cat([real_y, fake_y])
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y.squeeze().numpy(),
    )

    buffer = io.BytesIO()
    torch.save(
        {"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test},
        buffer,
    )
    buffer.seek(0)
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="rumour-milled",
        Key=f"runs/{run_id}/input/data.pt",
        Body=buffer.getvalue(),
    )

    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    model = SimpleHeadlineClassifier(768, 256, 1)
    loss_fn = nn.BCEWithLogitsLoss()
    optimiser = optim.Adam(model.parameters(), lr=lr)
    trainer = Trainer(model=model, loss_fn=loss_fn, optimiser=optimiser)
    trainer.train(
        train_loader=train_loader, validation_loader=val_loader, epochs=epochs
    )

    output_dir = os.environ.get("SM_MODEL_DIR")
    os.makedirs(output_dir, exist_ok=True)
    torch.save(trainer.model.state_dict(), os.path.join(output_dir, "model.pt"))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", type=str)
    ap.add_argument("--epochs", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--real-size", type=int, default=128)
    ap.add_argument("--fake-size", type=int, default=128)
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--random-state", type=int, default=42)
    args = ap.parse_args()
    main(
        args.run_id,
        args.epochs,
        args.lr,
        args.batch_size,
        args.real_size,
        args.fake_size,
        args.test_size,
        args.random_state,
    )
