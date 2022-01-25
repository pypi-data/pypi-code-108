import os
from itertools import product

import numpy as np
from torch.functional import Tensor


def pwd():
    return os.path.dirname(os.path.realpath(__file__))


def heatmap2points(x: Tensor) -> Tensor:
    """B x C x H x W -> B x C x 2"""
    out = torch.zeros((x.size(0), x.size(1), 2))
    conf = torch.zeros((x.size(0), x.size(1), 1))
    for b, c in product(range(x.size(0)), range(x.size(1))):
        conf[b, c] = torch.max(x[b, c])
        out[b, c] = (x[b, c] == conf[b, c]).nonzero(as_tuple=False)[0]
        out[b, c] /= torch.tensor([x.size(2), x.size(3)])
    return out, conf


# draw 2d gaussians
def draw_labelmap(img: np.ndarray, pt, sigma=3, type="Gaussian"):
    # Draw a 2D gaussian
    # Adopted from https://github.com/anewell/pose-hg-train/blob/master/src/pypose/draw.py
    pt[0], pt[1] = pt[1], pt[0]

    # Check that any part of the gaussian is in-bounds
    ul = [int(pt[0] - 3 * sigma), int(pt[1] - 3 * sigma)]
    br = [int(pt[0] + 3 * sigma + 1), int(pt[1] + 3 * sigma + 1)]

    # Generate gaussian
    size = 6 * sigma + 1
    x = np.arange(0, size, 1, float)
    y = x[:, np.newaxis]
    x0 = y0 = size // 2
    # The gaussian is not normalized, we want the center value to equal 1
    if type == "Gaussian":
        g = np.exp(-((x - x0) ** 2 + (y - y0) ** 2) / (2 * sigma ** 2))

    # Usable gaussian range
    g_x = max(0, -ul[0]), min(br[0], img.shape[1]) - ul[0]
    g_y = max(0, -ul[1]), min(br[1], img.shape[0]) - ul[1]
    # Image range
    img_x = max(0, ul[0]), min(br[0], img.shape[1])
    img_y = max(0, ul[1]), min(br[1], img.shape[0])

    img[img_y[0] : img_y[1], img_x[0] : img_x[1]] = g[g_y[0] : g_y[1], g_x[0] : g_x[1]]
    return img


import torch
from torch.functional import Tensor
from torchvision import utils


def tensorboard_plot_image(
    writer, x: Tensor, name: str, epoch: int, scale_each: bool = False
) -> None:
    """
    records single image into tensorboard.
    tensorboard logs are saved under lightning_logs.
    >>> SU.stensorboard_plot_image(
        self.logger.experiment,
        torch.cat([img1[:, :, -1], img2[:, :, -1]], dim=2),
        "recons",
        self.current_epoch,
    )
    """
    with torch.no_grad():
        x = x[:16].clone()
        grid = utils.make_grid(x, nrow=4, scale_each=scale_each, normalize=True)
        writer.add_image(name, grid, epoch)
