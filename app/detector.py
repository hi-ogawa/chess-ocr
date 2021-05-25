import torch
import torch.nn as nn
import torchvision.transforms.functional as VF
import cv2 as cv
import numpy as np
import PIL.Image as Image
from datetime import datetime
import random

#
# Piece Detection
#

LABELS = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK', 'empty']
FEN_PIECE_CHARS = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']


# [0, 1] -> [-1, 1]
normalize = lambda t: 2 * t - 1


def make_model():
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
        nn.Dropout(0.3),
        nn.Linear(128, 13)
    )


def predict8x8(model, image, log_dir=None):
    image = image.convert('L').resize([256, 256])
    x = VF.to_tensor(image)
    x = x.reshape([1, 8, 32, 8, 32]).permute([0, 1, 3, 2, 4]).reshape([64, 1, 32, 32])
    y = model(normalize(x))
    z, w = torch.max(torch.softmax(y, dim=-1), dim=-1)
    z = z.reshape([8, 8]).detach()
    w = w.reshape([8, 8]).detach()
    if log_dir is not None:
        for i, p, q in zip(range(64), x, w.reshape(64)):
            j = random.randrange(0, 10000)
            label = LABELS[q]
            timestamp = datetime.strftime(datetime.now(), "%F-%H-%M-%S")
            VF.to_pil_image(p).convert("RGB").save(f"{log_dir}/{label}--{timestamp}--{i:02d}--{j:04d}.png")
    return z, w


def to_fen(result):
    fen = ''
    cnt = 0
    for i in range(8):
        if i > 0:
            fen += '/'
        cnt = 0
        for j in range(8):
            piece = result[i][j]
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


#
# Board Detection
#

def detect_board(image, out_size):
    image = image.convert('L')
    image.thumbnail([800, 800])
    x = np.array(image)
    y = detect_edge(x)
    quad = detect_quad(y)
    if quad is None:
        raise RuntimeError('Board not detected')
    quad = order_vertices(quad)
    w, h = out_size
    square = np.array([[0, 0], [h, 0], [h, w], [0, w]])
    transform = cv.getPerspectiveTransform(quad.astype(np.float32), square.astype(np.float32))
    z = cv.warpPerspective(x, transform, (h, w))
    return Image.fromarray(z)


def detect_edge(x):
    # TODO: these parameters are too sensitive to given image...
    x = cv.GaussianBlur(x, (5, 5), 5)
    x = cv.Canny(x, 50, 50)
    x = cv.dilate(x, np.ones([3, 3], dtype=np.uint8))
    x = cv.erode(x, np.ones([2, 2], dtype=np.uint8))
    return x


def detect_quad(x):
    contours = cv.findContours(x, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[0]
    contours = sorted(contours, key = cv.contourArea, reverse = True)
    result = None
    for contour in contours:
        contour = cv.approxPolyDP(contour, cv.arcLength(contour, True) / 20, True)
        contour = contour.squeeze()
        if contour.shape[0] == 4:
            result = contour
            break
    return result


def order_vertices(vs):
    # counter-clock-wise from top-left
    if np.linalg.det(np.array([vs[1] - vs[0], vs[2] - vs[0]])) < 0:
        vs = np.flip(vs, axis=0)
    top_left = np.argmin(vs[:, 0] + vs[:, 1])
    vs = np.roll(vs, -top_left, axis=0)
    return vs


class Detector():
    def __init__(self, checkpoint_file, log_dir=None):
        self.model = make_model()
        self.model.load_state_dict(torch.load(checkpoint_file)['model_state_dict'])
        self.model.eval()
        self.log_dir = log_dir

    def detect_board(self, image):
        return detect_board(image, (256, 256))

    def board_to_fen(self, image):
        probability, labels = predict8x8(self.model, image, self.log_dir)
        return to_fen(labels)

    def detect(self, image):
        image = self.detect_board(image)
        fen = self.board_to_fen(image)
        return fen, image


def main(checkpoint_file, in_directory, out_directory):
    import pathlib
    detector = Detector(checkpoint_file, out_directory)
    in_path = pathlib.Path(in_directory)
    for ext in ["png", "jpg"]:
        for file in in_path.glob(f"*.{ext}"):
            detector.detect(Image.open(file))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint-file")
    parser.add_argument("--in-directory")
    parser.add_argument("--out-directory")
    main(**parser.parse_args().__dict__)
