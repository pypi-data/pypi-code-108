#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


__all__ = [
    "effective_impedance",
    "smooth",
    "meas2complex",
    "complex2aphi",
    "truncate",
    "Timer",
]

import time

import numpy as np
import scipy.signal as signal

from .constants import *


def effective_impedance(Z, epsilon, thickness, freq):
    k0 = 2 * pi * freq / c
    n = epsilon ** 0.5
    T = np.tan(k0 * n * thickness)
    z = Z0 / n
    return z * (Z + 1j * z * T) / (z + 1j * Z * T)


def smooth(data, cutoff=0.05, order=3):
    """Data smoothing.

    Parameters
    ----------
    data : array
        The data to smooth.
    cutoff : float
        Filter cutoff frequency (the default is 0.05).
    order : int
        Filter order (the default is 3).

    Returns
    -------
    smooth_data: array
        Smoothed data.

    """
    # Buterworth filter
    B, A = signal.butter(order, cutoff, output="ba")
    smooth_data = signal.filtfilt(B, A, data)
    return smooth_data


def meas2complex(A, phi):
    return 10 ** (A / 20) * np.exp(1j * phi * pi / 180)


def complex2aphi(z):
    return np.abs(z), np.unwrap(np.angle(z)) * 180 / pi


def truncate(freqs, min_freq, max_freq, dspl=0):
    return np.where(np.logical_and(freqs >= min_freq, freqs <= max_freq))[0][::dspl]


class TimerError(Exception):

    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self):

        self._start_time = None

    def start(self):
        """Start a new timer"""

        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
