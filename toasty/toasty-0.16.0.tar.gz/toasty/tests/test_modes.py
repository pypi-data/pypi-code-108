# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 the AAS WorldWide Telescope project
# Licensed under the MIT License.

import numpy as np
import pytest

from ..image import Image, ImageMode


class ModeInfo(object):
    def __init__(self, mode, dtype, demo_shape, default_format):
        self.mode = mode
        self.dtype = dtype
        self.demo_shape = demo_shape
        self.default_format = default_format


MODE_INFO = [
    ModeInfo(ImageMode.RGB, np.uint8, (10, 10, 3), "png"),
    ModeInfo(ImageMode.RGBA, np.uint8, (10, 10, 4), "png"),
    ModeInfo(ImageMode.F32, np.float32, (10, 10), "npy"),
    ModeInfo(ImageMode.F64, np.float64, (10, 10), "npy"),
    ModeInfo(ImageMode.F16x3, np.float16, (10, 10, 3), "npy"),
    ModeInfo(ImageMode.U8, np.uint8, (10, 10), "npy"),
    ModeInfo(ImageMode.I32, np.int32, (10, 10), "npy"),
]


def test_from_array_info():
    for mi in MODE_INFO:
        assert ImageMode.from_array_info(mi.demo_shape, mi.dtype) == mi.mode

    with pytest.raises(ValueError):
        s = (10, 10)
        ImageMode.from_array_info(s, np.complex64)

        s = (10, 10, 3)
        ImageMode.from_array_info(s, np.float32)

        s = (10, 10, 4)
        ImageMode.from_array_info(s, np.int8)


def test_image_interface():
    for mi in MODE_INFO:
        arr = np.zeros(mi.demo_shape, dtype=mi.dtype)
        img = Image.from_array(arr)
        img._default_format = None
        assert img.default_format == mi.default_format
        mb = mi.mode.make_maskable_buffer(8, 8)
        img.fill_into_maskable_buffer(
            mb, slice(1, 5), slice(1, 5), slice(4, 8), slice(4, 8)
        )

        mb.asarray().fill(1)
        img.update_into_maskable_buffer(
            mb, slice(1, 5), slice(1, 5), slice(4, 8), slice(4, 8)
        )
        assert mb.asarray().flat[0] == 1

        img.clear()
