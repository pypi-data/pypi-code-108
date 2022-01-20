#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 10-12-2020
           """

from enum import Enum
from functools import partial
from pathlib import Path

import numpy
import torchaudio
from draugr.torch_utilities import to_tensor
from draugr.numpy_utilities import get_sampler, normalise_signal
from matplotlib import pyplot
from numpy.fft import irfft, rfft


def white_noise(length: int, seed: int = None) -> numpy.ndarray:
    """
    White noise.

    * N: Amount of samples.

    White noise has a constant power density.
    Its narrowband spectrum is therefore flat.
    The power in white noise will increase by a factor of two for each octave band,
    and therefore increases with 3 dB per octave.

    """
    if seed:
        numpy.random.seed(seed)
    return numpy.random.randn(length)


def blue_noise(length: int, seed: int = None) -> numpy.ndarray:
    """
    Blue noise.

    * N: Amount of samples.

    Power increases with 6 dB per octave.
    Power density increases with 3 dB per octave.
    """
    x = rfft(white_noise(length, seed)) / length

    return normalise_signal(
        irfft(x * numpy.sqrt(numpy.arange(len(x)))).real[:length]  # Filter
    )


def brown_noise(length: int, seed: int = None) -> numpy.ndarray:
    """
    Brown noise.

    * N: Amount of samples.

    Power decreases with -3 dB per octave.
    Power density decreases with 6 dB per octave.

    """
    x = rfft(white_noise(length, seed)) / length
    return normalise_signal(
        irfft(x / (numpy.arange(len(x)) + 1)).real[:length]  # Filter
    )


def pink_noise(length: int, seed: int = None) -> numpy.ndarray:
    """
    Pink noise.

    :param length: Amount of samples.
    :param seed: State of PRNG.
    :type seed: :class:`numpy.random.RandomState`

    Pink noise has equal power in bands that are proportionally wide.
    Power density decreases with 3 dB per octave.

    """
    # This method uses the filter with the following coefficients.
    # b = numpy.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
    # a = numpy.array([1, -2.494956002, 2.017265875, -0.522189400])
    # return lfilter(B, A, numpy.random.randn(N))
    # Another way would be using the FFT
    # x = numpy.random.randn(N)
    # X = rfft(x) / N
    sampler = get_sampler(seed)
    uneven = length % 2
    x = sampler.randn(length // 2 + 1 + uneven) + 1j * sampler.randn(
        length // 2 + 1 + uneven
    )
    y = (
        irfft(x / numpy.sqrt(numpy.arange(len(x)) + 1.0))  # +1 to avoid divide by zero
    ).real
    if uneven:
        y = y[:-1]
    return normalise_signal(y)


def violet_noise(length: int, seed: int = None) -> numpy.ndarray:
    """
    Violet noise. Power increases with 6 dB per octave.

    :param length: Amount of samples.
    :param seed: State of PRNG.
    :type seed: :class:`numpy.random.RandomState`

    Power increases with +9 dB per octave.
    Power density increases with +6 dB per octave.

    """
    sampler = get_sampler(seed)
    uneven = length % 2
    x = sampler.randn(length // 2 + 1 + uneven) + 1j * sampler.randn(
        length // 2 + 1 + uneven
    )
    y = (irfft(x * numpy.arange(len(x)))).real  # Filter
    if uneven:
        y = y[:-1]
    return normalise_signal(y)


class GaussianNoiseTypeEnum(Enum):
    r""""""
    white = partial(
        white_noise
    )  # Partial to workaround interpreting as a method definition
    brown = partial(brown_noise)
    blue = partial(blue_noise)
    pink = partial(pink_noise)
    violet = partial(violet_noise)

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)


def generate_noise(
    length: int,
    *,
    seed: int = None,
    noise_type: GaussianNoiseTypeEnum = GaussianNoiseTypeEnum.white,
    export_path: Path = None,
    sampling_rate: int = 16000,
) -> numpy.ndarray:
    normalised = noise_type(length, seed)
    if export_path:
        torchaudio.save(str(export_path), to_tensor(normalised), sampling_rate)
    return normalised


if __name__ == "__main__":

    def asijsda():
        sampling_rate = 16000
        length_sec = 5
        noises = {}
        for a in GaussianNoiseTypeEnum:
            name = f"{a.name}_noise.wav"

            noise = generate_noise(
                sampling_rate * length_sec,
                seed=42,
                noise_type=a,
                export_path=Path("exclude") / name,
            )
            noises[name] = noise

        channels = numpy.array(list(noises.values()))
        channels = numpy.concatenate(
            [channels, normalise_signal(channels.sum(0, keepdims=True))]
        )
        channel_names = list(noises.keys()) + ["mixed"]
        from draugr import dissected_channel_plot

        dissected_channel_plot(
            channels,
            channel_names=channel_names,
            sampling_rate=sampling_rate,
            max_resolution=16000,
        )
        pyplot.show()

    asijsda()
