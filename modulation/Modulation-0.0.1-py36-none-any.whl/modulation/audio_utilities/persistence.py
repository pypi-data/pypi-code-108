#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 17-12-2020
           """

import os

import numpy
import soundfile
from typing import Any, Sequence, Tuple


def audio_read(
    path: str, norm: bool = True, start: int = 0, stop: int = None
) -> Tuple[numpy.ndarray, int]:
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise ValueError(f"[{path}] does not exist!")
    try:
        x, sr = soundfile.read(path, start=start, stop=stop)
        if len(x.shape) == 1:  # mono
            if norm:
                rms = (x ** 2).mean() ** 0.5
                scalar = 10 ** (-25 / 20) / rms
                x = x * scalar
            return x, sr
        else:  # multi-channel
            x = x.T
            x = x.sum(axis=0) / x.shape[0]
            if norm:
                rms = (x ** 2).mean() ** 0.5
                scalar = 10 ** (-25 / 20) / rms
                x = x * scalar
            return x, sr
    except RuntimeError:  # fix for sph pcm-embedded shortened v2
        print("WARNING: Audio type not supported")


def audio_write(
    data: numpy.ndarray, fs: int, dest_path: str, norm: bool = False
) -> None:
    if norm:
        rms = (data ** 2).mean() ** 0.5
        scalar = 10 ** (-25 / 10) / (rms + numpy.eps)
        data = data * scalar
        if max(abs(data)) >= 1:
            data = data / max(abs(data), numpy.eps)

    dest_path = os.path.abspath(dest_path)
    destdir = os.path.dirname(dest_path)

    if not os.path.exists(destdir):
        os.makedirs(destdir)

    soundfile.write(dest_path, data, fs)
