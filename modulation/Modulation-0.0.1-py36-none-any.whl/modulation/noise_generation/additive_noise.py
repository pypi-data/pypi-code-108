#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 10-12-2020
           """

from pathlib import Path
from typing import Any

import numpy
import scipy.signal as scipy_signal
from draugr.numpy_utilities import root_mean_square
from scipy.io import wavfile
from draugr.tqdm_utilities import progress_bar
from apppath import ensure_existence

from modulation.audio_utilities.splitting import mask_split_speech_silence


def sample_noise(
    noise,
    noise_rate: int,
    signal_len: int,
    signal_rate: int,
    *,
    resample_noise: bool = True,
) -> Any:
    noise_len = len(noise)
    if resample_noise:
        noise = scipy_signal.resample(
            noise, round(noise_len * float(signal_rate) / noise_rate)
        )

    start_index = numpy.random.randint(0, noise_len)
    noise = numpy.tile(noise, (signal_len // noise_len) + 2)  # at least tile once (=2)
    return noise[start_index : signal_len + start_index]


def compute_additive_noise_samples(
    *,
    voice_activity_mask: numpy.ndarray,
    signal_file: Path,
    category,
    out_dir,
    noise_file,
    snrs=list((i * 5 for i in range(5))),
    verbose: bool = False,
) -> None:
    sr_noise, noise = wavfile.read(str(noise_file))
    sr_signal, signal = wavfile.read(str(signal_file))

    max_sample = numpy.max(signal)
    signal = signal / max_sample

    noise_part = sample_noise(
        noise / numpy.max(noise),
        noise_rate=sr_noise,
        signal_len=len(signal),
        signal_rate=sr_signal,
    )

    noise_scaled = noise_part * (
        root_mean_square(mask_split_speech_silence(voice_activity_mask, signal)[0])
        / root_mean_square(noise_part)
    )  # scaled by ratio of speech to noise level

    for snr in progress_bar(snrs, disable=not verbose):
        noised = signal + noise_scaled / (10 ** (snr / 20))
        dest = str(
            ensure_existence(
                out_dir / f'{noise_file.with_suffix("").name}_SNR_{snr}dB' / category
            )
            / signal_file.name
        )
        if verbose:
            print(f"writing wavfile {dest}")
        wavfile.write(
            dest,
            sr_signal,
            ((noised / numpy.max(noised)) * max_sample).astype(numpy.int16),
        )


if __name__ == "__main__":
    pass
