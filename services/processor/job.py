from rumour_milled.ml.load import load_headlines
from rumour_milled.ml.preprocess import tokenise_and_vectorise
from boto3.dynamodb.conditions import Attr
from sklearn.model_selection import train_test_split
from datetime import datetime, timezone
import uuid
import argparse
import torch
import os


def main():
    run_id = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}-{uuid.uuid4().hex[:6]}"

    ap = argparse.ArgumentParser()
    ap.add_argument("--fake-size", type=int, default=256)
    ap.add_argument("--real-size", type=int, default=256)
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--random-state", type=int, default=42)
    args = ap.parse_args()

    real_headlines, _ = load_headlines(
        filter_expression=Attr("label").eq(0), max_items=args.real_size
    )
    fake_headlines, _ = load_headlines(
        filter_expression=Attr("label").eq(1), max_items=args.fake_size
    )
    headlines = real_headlines + fake_headlines
    X = tokenise_and_vectorise(headlines, batch_size=128)
    real_y = torch.zeros((args.real_size, 1))
    fake_y = torch.ones((args.fake_size, 1))
    y = torch.cat([real_y, fake_y])
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y.squeeze().numpy(),
    )

    output_dir = "/opt/ml/processing/train"
    os.makedirs(output_dir, exist_ok=True)
    torch.save(
        {"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test},
        os.path.join(output_dir, "data.pt"),
    )


if __name__ == "__main__":
    main()
