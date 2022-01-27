# -*- mode: python; coding: utf-8 -*-
# Copyright 2020 the AAS WorldWide Telescope project
# Licensed under the MIT License.

"""
Loading OpenEXR files.

This is very primitive support. Implemented for:

https://svs.gsfc.nasa.gov/4851

"""
from __future__ import absolute_import, division, print_function

__all__ = '''
load_openexr
'''.split()

import numpy as np
import sys


def load_openexr(path):
    """
    Load an OpenEXR file

    Parameters
    ----------
    path : path-like
        The path to the file

    Returns
    -------
    An image-like Numpy array with shape ``(height, width, planes)``
    and a dtype of float16 or float32. (Toasty only fully supports float16.)

    """
    try:
        import OpenEXR
        import Imath
    except ImportError as e:
        raise Exception('cannot load OpenEXR file: needed support libraries are not available') from e

    EXR_TO_NUMPY = {
        Imath.PixelType.FLOAT: np.float32,
        Imath.PixelType.HALF: np.float16,
    }

    exr = OpenEXR.InputFile(path)
    header = exr.header()
    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1

    if header['lineOrder'] != Imath.LineOrder(Imath.LineOrder.INCREASING_Y):
        raise Exception('cannot load OpenEXR file: unsupported lineOrder')
    if len(header['channels']) != 3:
        raise Exception('cannot load OpenEXR file: expected exactly 3 channels')
    if 'chromaticities' in header:
        print('warning: ignoring chromaticities in OpenEXR file; colors will be distorted',
              file=sys.stderr)
    if 'whiteLuminance' in header:
        print('warning: ignoring whiteLuminance in OpenEXR file; colors will be distorted',
              file=sys.stderr)

    img = None

    try:
        for idx, chan in enumerate('RGB'):
            ctype = header['channels'][chan].type
            cbytes = exr.channel(chan)
            dtype = EXR_TO_NUMPY[ctype.v]

            if img is None:
                img = np.empty((height, width, 3), dtype=dtype)

            img[...,idx] = np.frombuffer(cbytes, dtype=dtype).reshape((height, width))
    except Exception as e:
        raise Exception('cannot load OpenEXR file: unexpected file structure') from e

    return img
