import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as VT
import torchvision.transforms.functional as VF
import torchmetrics
import pytorch_lightning as pl
import pytorch_lightning.utilities.cli
import PIL.Image as Image

import pathlib
from functools import partial

from .model import LABELS, make_model, normalize, to_loss, to_pred, to_prob, to_prob_pred


def random_noise(t, mean=0, std=1):
    return t + mean + torch.randn(t.size(), device=t.device) * std


def make_augmentation():
    return VT.Compose([
        VT.RandomApply([VT.GaussianBlur(3)], p=0.5),
        VT.RandomAffine(30, (0.3, 0.3), (0.7, 1.3), [-5, 5]),
        VT.RandomApply([partial(random_noise, std=0.1)], p=0.5),
        lambda x: VF.adjust_brightness(x, torch.empty(1).uniform_(0.7, 1.3)),
    ])


class Dataset():
    def __init__(self, directory):
        self.files = sorted(pathlib.Path(directory).glob('*.png'))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        file = self.files[i]
        image = Image.open(file)
        assert image.mode == 'RGB'
        image = image.convert('L')
        x = VF.to_tensor(image)
        label = file.name.split('--')[0]
        y = torch.tensor(LABELS.index(label), dtype=torch.int64)
        return x, y


class DataModule(pl.LightningDataModule):
    def __init__(self, directory: str, directory_extra = None, batch_size=32, val_fraction=0.05, num_workers=0):
        super().__init__()
        self.dataset = Dataset(directory)
        if directory_extra:
            self.dataset = torch.utils.data.ConcatDataset([self.dataset, Dataset(directory_extra)])
        self.loader_kwargs = dict(batch_size=batch_size, num_workers=num_workers)
        len_total = len(self.dataset)
        len_val = int(val_fraction * len_total)
        len_train = len_total - len_val
        self.train_dataset, self.val_dataset = torch.utils.data.random_split(self.dataset, [len_train, len_val])

    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train_dataset, **self.loader_kwargs)

    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.val_dataset, **self.loader_kwargs)


class LitModel(pl.LightningModule):
    def __init__(self, lr=0.001, lr_step=40, lr_gamma=0.1, augmentation=True, dropout=0.3):
        super().__init__()
        self.save_hyperparameters()
        self.model = make_model(dropout)
        self.augment = make_augmentation() if augmentation else None
        self.train_acc = torchmetrics.Accuracy()
        self.val_acc = torchmetrics.Accuracy()

    def forward(self, x):
        return self.model(normalize(x))

    def on_train_epoch_start(self):
        self.train_acc.reset()

    def training_step(self, batch, batch_idx):
        x, y = batch
        if self.augment:
            x = self.augment(x)
        y_hat = self.forward(x)
        loss = to_loss(y_hat, y)
        self.train_acc(to_pred(y_hat), y)
        self.log("train_acc", self.train_acc.compute(), on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def on_validtion_epoch_start(self):
        self.val_acc.reset()

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self.forward(x)
        loss = to_loss(y_hat, y)
        self.val_acc(to_pred(y_hat), y)
        self.log("val_acc", self.val_acc.compute(), on_step=False, on_epoch=True, prog_bar=True)

    def configure_optimizers(self):
        opt = torch.optim.Adam(self.model.parameters(), lr=self.hparams.lr)
        sch = torch.optim.lr_scheduler.StepLR(opt, step_size=self.hparams.lr_step, gamma=self.hparams.lr_gamma, verbose=True)
        return {
            "optimizer": opt,
            "lr_scheduler": { "scheduler": sch }
        }


if __name__ == '__main__':
    cli = pl.utilities.cli.LightningCLI(LitModel, DataModule, seed_everything_default=0x12345678)
