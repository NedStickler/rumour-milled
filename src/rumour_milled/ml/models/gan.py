import torch.nn as nn


class HeadlinesGenerator(nn.Module):
    def __init__(self, noise_dim, hidden_dim, sentence_dim):
        super(HeadlinesGenerator, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(noise_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, sentence_dim),
            nn.Tanh(),
        )

    def forward(self, x):
        return self.net(x)


class HeadlinesDiscriminator(nn.Module):
    def __init__(self, sentence_dim, hidden_dim):
        super(HeadlinesDiscriminator, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(sentence_dim, hidden_dim),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)
