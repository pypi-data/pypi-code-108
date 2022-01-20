#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 09/04/2020
           """

import numpy


def fft_denoise(
    noisy_signal: numpy.ndarray, num_time_steps: int, cutoff_threshold: float = 100
) -> numpy.ndarray:
    """"""

    noisy_signal_f_coef = numpy.fft.fft(
        noisy_signal, num_time_steps
    )  # Frequency coefficients in frequency space
    power_spectral_density = (
        noisy_signal_f_coef * numpy.conj(noisy_signal_f_coef) / num_time_steps
    )  # PSD

    indices = power_spectral_density > cutoff_threshold  # 1 for true, 0 for false

    return numpy.fft.ifft(
        noisy_signal_f_coef * indices
    )  # Inverse to signal space, cleaned
