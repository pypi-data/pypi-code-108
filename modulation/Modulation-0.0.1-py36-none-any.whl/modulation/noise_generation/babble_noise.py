#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 09-12-2020
           """

from pathlib import Path
from typing import Iterable, Sequence

import numpy
import torchaudio

from draugr.torch_utilities import to_tensor

from draugr.numpy_utilities.signal_utilities.truncation import min_length_truncate_batch

__all__ = ["generate_babble_noise"]


def generate_babble_noise(
    samples: Iterable[Iterable[Sequence]],
    sampling_rate: int,
    *,
    export_path: Path = None,
) -> Iterable:
    samples = numpy.array(min_length_truncate_batch(samples))
    mixed = numpy.sum(samples / numpy.max(numpy.abs(samples)), 0)
    if export_path:
        torchaudio.save(str(export_path), to_tensor(mixed), sampling_rate)
    return mixed


if __name__ == "__main__":

    def main():
        from modulation.data.audio.speech.recognition.libri_speech import LibriSpeech
        from draugr.visualisation import dissected_channel_plot

        samples = 4
        from matplotlib import pyplot

        libri_speech = LibriSpeech(
            path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech"
        )
        files, sr = zip(
            *[(v[0].numpy(), v[1]) for _, v in zip(range(samples), libri_speech)]
        )
        assert all([sr[0] == s for s in sr[1:]])
        babble = generate_babble_noise(
            files, sr[0], export_path=Path("exclude") / "babble.wav"
        )

        c_names = (*(f"C{i}" for i in range(len(files))), "mixed")
        files = (*files, babble)
        files = numpy.array(min_length_truncate_batch(files)).squeeze(1)

        dissected_channel_plot(
            files, title=f"{samples} sample babble", channel_names=c_names
        )
        pyplot.show()

    main()
