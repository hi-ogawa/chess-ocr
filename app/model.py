import torch
import torch.nn as nn
import torch.nn.functional as F


LABELS = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK', 'empty']
OUT_SIZE = len(LABELS)


# [0, 1] -> [-1, 1]
def normalize(t):
    return 2 * t - 1


def make_model(dropout):
    return nn.Sequential(
        nn.Conv2d(1, 32, kernel_size=3),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, kernel_size=3),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(64, 128, kernel_size=3),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Dropout(dropout),
        nn.Linear(128, OUT_SIZE)
    )


def to_loss(y, z):
    return F.cross_entropy(y, z)


def to_pred(y):
    return y.argmax(dim=-1)


def to_prob(y):
    return torch.max(F.softmax(y, dim=-1), dim=-1).values


def to_prob_pred(y):
    return torch.max(F.softmax(y, dim=-1), dim=-1)
