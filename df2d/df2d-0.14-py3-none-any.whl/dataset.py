from typing import *

import matplotlib.pyplot as plt
import numpy as np
import torch
from skimage.color import gray2rgb
from skimage.transform import resize

from df2d.util import draw_labelmap


class Drosophila2Dataset(torch.utils.data.Dataset):
    def __init__(
        self,
        inp: List[List[Union[str, np.ndarray]]],
        load_f: Callable = lambda x: plt.imread(x),
        img_size: List[int] = [256, 512],
        heatmap_size: List[int] = [64, 128],
        heatmap_channels: int = 19,
        return_heatmap: bool = False,
    ):
        self.inp = inp
        self.load_f = load_f
        self.img_size = img_size
        self.heatmap_size = heatmap_size
        self.return_heatmap = return_heatmap
        self.heatmap_channels = heatmap_channels

    def __getitem__(self, idx):
        img_path, pts2d = self.inp[idx]
        img = self.load_f(img_path)
        img = resize(img, self.img_size)

        # gray2rgb
        if img.ndim == 2:
            img = gray2rgb(img)

        # h w c -> c h w
        img = img.transpose(2, 0, 1)

        # remove the mean
        img = img - 0.22

        # draw heatmap
        if self.return_heatmap:
            hm = np.zeros(
                (self.heatmap_channels, self.heatmap_size[0], self.heatmap_size[1])
            )
            present_joints = [
                idx
                for idx in range(self.heatmap_channels)
                if not np.all(pts2d[idx] == 0)
            ]
            for idx in present_joints:
                hm[idx] = draw_labelmap(
                    hm[idx], pts2d[idx]  * np.array(self.heatmap_size)
                )

        if self.return_heatmap:
            return img, pts2d, tuple(self.inp[idx]), hm
        else:
            return img, pts2d, tuple(self.inp[idx])

    def __len__(self):
        return len(self.inp)
