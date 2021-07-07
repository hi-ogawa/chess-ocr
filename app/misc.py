import torch
import torchvision.transforms.functional as VF
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image as Image


def imshow(x, ax=plt):
    if isinstance(x, np.ndarray):
        x = Image.fromarray(x)
    if isinstance(x, torch.Tensor):
        x = torch.clamp(x, 0, 1)
        x = VF.to_pil_image(x)
    x = x.convert('RGB')
    ax.imshow(x)
