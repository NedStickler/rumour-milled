import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.modules.loss import _Loss
from torch.utils.data import TensorDataset, DataLoader
from typing import Optional


def train_model(
    X: torch.Tensor,
    y: torch.Tensor,
    model: nn.Module,
    criterion: nn.modules.loss._Loss,
    optimiser: optim.Optimizer,
    model_kwargs: dict,
    batch_size: int = 32,
    shuffle: bool = True,
    device: Optional[str] = None,
    learning_rate: float = 0.001,
    epochs: int = 10,
):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = TensorDataset(X, y)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
    model = model(**model_kwargs).to(device)
    optimiser = optimiser(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        total_loss = 0
        for batch_X, batch_y in data_loader:
            optimiser.zero_grad()
            logits = model(batch_X.to(device))
            loss = criterion(logits, batch_y.to(device))
            loss.backward()
            optimiser.step()
            total_loss += loss.item()
