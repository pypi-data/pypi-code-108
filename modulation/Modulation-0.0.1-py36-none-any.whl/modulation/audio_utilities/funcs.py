#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 11-01-2021
           """

import numpy
import torch
from draugr import next_pow_2
from scipy.signal import lfilter, hilbert

from typing import Sequence, Iterable, Callable, Union
from functools import reduce

from warg import Number, identity


def mel_scale(x):
    return 2595.0 * numpy.log10(1.0 + x / 700.0)


def in_mel_scale(x):
    return 700 * (10 ** (x / 2595.0) - 1)


def pre_emphasise(x, coeff: float = 0.97):
    return lfilter([1, -coeff], [1], x)


def de_emphasise(x, coeff: float = 0.97):
    return lfilter([1], [1, -coeff], x)


def pre_emphasise_torch(signal, preemph: float = 0.97):
    """
    Pre-emphasis on the input signal
    :param signal: (time,)
    :param preemph:
    :return: (time,)
    """
    return torch.cat((signal[0:1], signal[1:] - preemph * signal[:-1]))


def fft_frequencies(sr=16000, n_fft=512):
    return numpy.linspace(0, float(sr) / 2, int(1 + n_fft // 2), endpoint=True)


def hilbert_envelope(signal: numpy.ndarray, *, n_fft: int = None) -> numpy.ndarray:
    """Calculates the Hilbert envelope of a signal.

    Parameters
    ----------
    signal : array_like
        Signal on which to calculate the hilbert envelope. The calculation
        is done along the last axis (i.e. ``axis=-1``).

    Returns
    -------
    ndarray

    """
    signal_length = signal.shape[-1]
    if not n_fft:
        n_fft = next_pow_2(signal_length)
    return numpy.abs(
        hilbert(signal, n_fft)[..., :signal_length]
    )  # Return signal with same shape as original


class SignalGenerator:
    def __init__(self, *funcs: Union[Callable, Number], delta_time: float = 1.0):
        self.reset_internal_time()
        self.delta_time = delta_time
        self.funcs = (0, *funcs)

    def __iter__(self):
        self.reset_internal_time()
        return self

    def __next__(self):
        self.t += self.delta_time
        return self.apply(self.t)

    def apply(self, t: float) -> float:
        return reduce(lambda x, y: x + y(t), self.funcs)

    def __call__(self, t: Iterable[Number]) -> Sequence:
        return [self.apply(i) for i in t]

    def reset_internal_time(self):
        self.t = 0.0

    def set_internal_time(self, t):
        self.t = t

    def __enter__(self):
        self.reset_internal_time()
        return True


if __name__ == "__main__":
    # print(mel_scale(numpy.arange(9)**2))
    # print(len(fft_frequencies())) # oneside
    # print(len(numpy.fft.fftfreq(512)))
    def aijsda():
        a = list(range(1, 9 + 1))
        b = pre_emphasise(a)
        c = de_emphasise(b)
        assert numpy.allclose(a, c), print(a, "\n", c)

    def asidjashdya():
        a = SignalGenerator(identity)
        for _, i in zip(range(10), a):
            print(i)

    asidjashdya()
    # aijsda()
