import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms.functional as VF


LABELS = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK', 'empty']
FEN_PIECE_CHARS = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
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


def predict_8x8(forward, image):
    image = image.convert('L')
    image = image.resize([256, 256])
    x = VF.to_tensor(image)
    x = x.reshape([1, 8, 32, 8, 32]).permute([0, 1, 3, 2, 4]).reshape([64, 1, 32, 32])
    y = forward(x)
    prob, pred = to_prob_pred(y)
    prob = prob.reshape([8, 8]).detach()
    pred = pred.reshape([8, 8]).detach()
    return prob, pred


def to_fen(prediction_8x8):
    fen = ''
    cnt = 0
    for i in range(8):
        if i > 0:
            fen += '/'
        cnt = 0
        for j in range(8):
            piece = prediction_8x8[i][j]
            if piece == 12:
                cnt += 1
            else:
                if cnt > 0:
                    fen += str(cnt)
                fen += FEN_PIECE_CHARS[piece]
                cnt = 0
        if cnt > 0:
            fen += str(cnt)
    return fen


def predict_fen(forward, image):
    prob, pred = predict_8x8(forward, image)
    return to_fen(pred)
