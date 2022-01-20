#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 30-12-2020
           """

import math
from typing import Iterable

import numpy
import torchaudio
from draugr.torch_utilities import to_tensor

from modulation.audio_utilities.signal_statistics import root_mean_square


def additive_white_noise(
    signal, signal_noise_ratio, sampling_rate, export_path=None
) -> Iterable:
    noise = numpy.random.normal(
        0,
        math.sqrt(root_mean_square(signal) ** 2 / (pow(10, signal_noise_ratio / 10))),
        signal.shape[-1],
    )
    if export_path:
        torchaudio.save(str(export_path), to_tensor(noise), sampling_rate)
    return noise


if __name__ == "__main__":

    def asda():
        from modulation.data.audio.speech.recognition.libri_speech import LibriSpeech
        from pathlib import Path

        libri_speech = LibriSpeech(
            path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech"
        )
        files, sr = zip(*[(v[0].numpy(), v[1]) for _, v in zip(range(1), libri_speech)])
        assert all([sr[0] == s for s in sr[1:]])
        additive_white_noise(
            files[0],
            10,
            sr[0],
            export_path=Path("exclude") / "white_gaussian_noise.wav",
        )

    asda()
