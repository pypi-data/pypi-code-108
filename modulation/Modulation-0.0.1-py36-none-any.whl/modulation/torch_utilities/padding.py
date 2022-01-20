#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 01-12-2020
           """

from typing import Iterable, Sequence, Tuple

import torch
from torch.nn import functional

from draugr.torch_utilities import to_tensor
from warg import Number

__all__ = ["batch_pad", "pad_sequence", "min_length_pad"]


def batch_pad(image_batch: Sequence, mask_batch: Sequence) -> Tuple[Sequence, Sequence]:
    """

    :param image_batch:
    :param mask_batch:
    :return:
    """
    # Determine maximum height and width
    # The mask's have the same height and width
    # since they mask the image.
    max_height = max([img.size(1) for img in image_batch])
    max_width = max([img.size(2) for img in image_batch])

    image_batch = [
        # The needed padding is the difference between the
        # max width/height and the image's actual width/height.
        functional.pad(img, [0, max_width - img.size(2), 0, max_height - img.size(1)])
        for img in image_batch
    ]
    mask_batch = [
        # Same as for the images, but there is no channel dimension
        # Therefore the mask's width is dimension 1 instead of 2
        functional.pad(
            mask, [0, max_width - mask.size(1), 0, max_height - mask.size(0)]
        )
        for mask in mask_batch
    ]

    return image_batch, mask_batch


def pad_sequence(batch: Iterable[torch.Tensor]) -> torch.Tensor:
    """

    :param batch:
    :return:
    """
    batch = [item.t() for item in batch]  # Transpose 2d
    batch = torch.nn.utils.rnn.pad_sequence(
        batch, batch_first=True, padding_value=0.0
    )  # Make all tensor in a batch the same length by padding with zeros
    return batch.permute(0, 2, 1)


def min_length_pad(
    sequence: torch.Tensor, min_length: int, padding_value: Number = 0
) -> torch.Tensor:
    """

    :param sequence:
    :param min_length:
    :param padding_value:
    :return:
    """
    out_dims = sequence.shape
    length = out_dims[-1]
    if length < min_length:
        out_dims = (*out_dims[:-1], min_length)
        out_tensor = sequence.new_full(
            out_dims, padding_value
        )  # .data.new(*out_dims).fill_(padding_value)
        out_tensor[..., :length] = sequence
        return out_tensor
    return sequence


if __name__ == "__main__":

    def a():
        base = 5
        stair_length = 9
        stair = [to_tensor(range(i + base)) for i in range(stair_length)]

        pad = [min_length_pad(s, stair_length + base) for s in stair]
        print(to_tensor(pad))

    a()
