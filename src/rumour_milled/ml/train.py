import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.modules.loss import _Loss
from torch.utils.data import TensorDataset, DataLoader
from typing import Optional


class Trainer:
    def __init__(
        self,
        model,
        loss_fn,
        optimiser,
        device,
    ):
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = model.to(device)
        self.loss_fn = loss_fn
        self.optimiser = optimiser

    def train_step(self, X, y):
        X, y = X.to(self.device), y.to(self.device)
        self.optimiser.zero_grad()
        out = self.model(X)
        loss = self.loss_fn(out, y)
        loss.backward()
        self.optimiser.step()
        return loss.item()

    def epoch_step(self, train_loader):
        self.model.train()
        epoch_loss = 0
        for X, y in train_loader:
            loss = self.train_step(X, y)
            epoch_loss += loss
        return epoch_loss / len(train_loader)

    def train(self, train_loader, validation_loader, epochs):
        for epoch in range(epochs):
            loss = self.epoch_step(train_loader)
            print(f"Epoch {epoch} loss: {loss}")

    def evaluate(self):
        return
