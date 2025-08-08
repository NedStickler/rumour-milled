import torch


# TODO:
# - Model saving with S3


class Trainer:
    def __init__(
        self,
        model,
        loss_fn,
        optimiser,
        scheduler=None,
        device=None,
    ):
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = model.to(self.device)
        self.loss_fn = loss_fn
        self.optimiser = optimiser
        self.scheduler = scheduler

    def train_batch(self, X, y):
        X, y = X.to(self.device), y.to(self.device)
        self.optimiser.zero_grad()
        out = self.model(X)
        loss = self.loss_fn(out, y)
        loss.backward()
        self.optimiser.step()
        return loss.item()

    def train_epoch(self, train_loader):
        self.model.train()
        epoch_loss = 0
        for X, y in train_loader:
            loss = self.train_batch(X, y)
            epoch_loss += loss
        return epoch_loss / len(train_loader)

    def train(self, train_loader, validation_loader, epochs):
        for epoch in range(1, epochs + 1):
            train_loss = self.train_epoch(train_loader)
            output_str = f"Epoch {epoch}/{epochs} | train_loss: {train_loss}"

            if validation_loader:
                val_loss = self.evaluate(validation_loader)
                output_str += f" | val_loss: {val_loss}"
            if self.scheduler:
                self.scheduler.step()
                output_str += f" | lr: {self.scheduler.get_last_lr()[0]}"

            print(output_str)

    def evaluate(self, validation_loader):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for X, y in validation_loader:
                X, y = X.to(self.device), y.to(self.device)
                out = self.model(X)
                loss = self.loss_fn(out, y)
                total_loss += loss.item()
        return total_loss / len(validation_loader)
