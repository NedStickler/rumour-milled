from rumour_milled.ml.models.simple import SimpleHeadlineClassifier
from rumour_milled.ml.train import Trainer
from torch.utils.data import TensorDataset, DataLoader
import torch
import torch.nn as nn
import torch.optim as optim
import os


# TODO:
# - Change hardcoded model/loss/optimiser


def main(epochs, lr, batch_size):
    input_dir = os.environ.get("SM_CHANNEL_DATA")
    blob = torch.load(os.path.join(input_dir, "data.pt"), map_location="cpu")

    train_dataset = TensorDataset(blob["X_train"], blob["y_train"])
    val_dataset = TensorDataset(blob["X_test"], blob["y_test"])

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
    ap.add_argument("--epochs", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--batch-size", type=int, default=32)
    args = ap.parse_args()
    main(args.epochs, args.lr, args.batch_size)
