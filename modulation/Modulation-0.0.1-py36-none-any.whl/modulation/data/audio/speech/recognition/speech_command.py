#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 18-11-2020
           """

from pathlib import Path
from typing import List

import torch
from torchaudio.datasets import SPEECHCOMMANDS

from draugr.numpy_utilities import SplitEnum

__all__ = ["SpeechCommands"]


class SpeechCommands(SPEECHCOMMANDS):
    """

    We use torchaudio to download and represent the dataset. Here we use
    `SpeechCommands <https://arxiv.org/abs/1804.03209>`__, which is a
    datasets of 35 commands spoken by different people. The dataset
    ``SPEECHCOMMANDS`` is a ``torch.utils.data.Dataset`` version of the
    dataset. In this dataset, all audio files are about 1 second long (and
    so about 16000 time frames long).

    The actual loading and formatting steps happen when a data point is
    being accessed, and torchaudio takes care of converting the audio files
    to tensors. If one wants to load an audio file directly instead,
    ``torchaudio.load()`` can be used. It returns a tuple containing the
    newly created tensor along with the sampling frequency of the audio file
    (16kHz for SpeechCommands).

    Going back to the dataset, here we create a subclass that splits it into
    standard training, validation, testing subsets.

    A data point in the SPEECHCOMMANDS dataset is a tuple made of a waveform
    (the audio signal), the sample rate, the utterance (label), the ID of
    the speaker, the number of the utterance.

    """

    def __init__(
        self,
        path: Path = Path.home() / "Data" / "Audio" / "Speech" / "SpeechCommands",
        *,
        split: SplitEnum = None,
        version: str = "speech_commands_v0.02"
    ):
        super().__init__(str(path.parent), download=False)  # Bad constructor, *bwahh'r*

        def load_list(filename: str):
            data_path = Path(self._path)
            filepath = data_path / filename
            with open(filepath) as f:
                return [str(data_path / line.strip()) for line in f]

        if split == SplitEnum.validation:
            self._walker = load_list("validation_list.txt")
        elif split == SplitEnum.testing:
            self._walker = load_list("testing_list.txt")
        elif split == SplitEnum.training:
            a = set(
                load_list("validation_list.txt") + load_list("testing_list.txt")
            )  # cache
            self._walker = [w for w in self._walker if w not in a]
        elif split is None:
            pass  # no splitting, do not modify walker
        else:
            raise Exception

        # a = set(e[2] for _,e in zip(range(99999),self)) # does not scale!!!
        a = [cat.name for cat in (path / version).iterdir() if cat.is_dir()]
        self._categories = sorted(set(a))

    @property
    def categories(self) -> List:
        return self._categories

    def label_to_index(self, word: str) -> torch.Tensor:
        # Return the position of the word in labels
        return torch.tensor(self.categories.index(word))

    def index_to_label(self, index: int) -> str:
        # Return the word corresponding to the index in labels
        # This is the inverse of label_to_index
        return self.categories[index]

    def __iter__(self):
        for idx in range(len(self)):
            yield self.__getitem__(idx)


if __name__ == "__main__":

    def asda():
        train_set = SpeechCommands(split=SplitEnum.training)
        print(train_set.categories)
        a = torch.utils.data.DataLoader(
            train_set, batch_size=1, shuffle=False, num_workers=0
        )
        for i, s in zip(range(2), a):
            print(i, s)
        for i, s in zip(range(2), train_set):
            print(i, s)

    asda()
