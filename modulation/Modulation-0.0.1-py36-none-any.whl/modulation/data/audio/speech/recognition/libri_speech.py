#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 10-12-2020
           """

from pathlib import Path

from torchaudio.datasets import LIBRISPEECH

from draugr.numpy_utilities import SplitIndexer, SplitEnum
from draugr import symbol_filter, FilterModeEnum
from enum import Enum
import csv


class LibriSpeech(LIBRISPEECH):
    class LibriSpeechSubsets(Enum):
        dev_clean = "dev-clean"
        dev_other = "dev-other"
        test_clean = "test-clean"
        test_other = "test-other"
        train_clean_100 = "train-clean-100"
        train_clean_360 = "train-clean-360"
        train_other_500 = "train-other-500"

    class CustomSubsets(Enum):
        male = "M"
        female = "F"
        # TODO: add more like Splits ...

    def __init__(
        self,
        *,
        path: Path = Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech",
        split: SplitEnum = None,
        subset: LibriSpeechSubsets = LibriSpeechSubsets.train_clean_100,
        custom_subset: CustomSubsets = None
    ):
        super().__init__(str(path), download=False, url=subset.value)

        gender_pool = {"M": [], "F": []}
        if (
            custom_subset == LibriSpeech.CustomSubsets.male
            or custom_subset == LibriSpeech.CustomSubsets.female
        ):
            with open(path / "LibriSpeech" / "SPEAKERS.txt") as f:
                reader = csv.DictReader(
                    symbol_filter(f, ";", exclusion_mode=FilterModeEnum.exclude_fully),
                    delimiter="|",
                    quoting=csv.QUOTE_NONE,
                    fieldnames=("ID", "SEX", "SUBSET", "MINUTES", "NAME"),
                )
                subset_idx_gender = {}
                for row in reader:
                    if subset.value == row["SUBSET"].strip():
                        subset_idx_gender[int(row["ID"].strip())] = row["SEX"].strip()
                for k, v in subset_idx_gender.items():
                    gender_pool[v].append(k)
            a = gender_pool[custom_subset.value]
            self._walker = [w for w in self._walker if int(w.split("-")[0]) in a]

        speaker_id_pool = list(i for o in gender_pool.values() for i in o)  # flattening

        speaker_indexer = SplitIndexer(len(speaker_id_pool))

        if split == SplitEnum.validation:
            pass
            # self._walker = load_list("validation_list.txt")
        elif split == SplitEnum.testing:
            pass
            # self._walker = load_list("testing_list.txt")
        elif split == SplitEnum.training:
            pass
            # self._walker = [w for w in self._walker if w not in set(load_list("validation_list.txt") + load_list("testing_list.txt"))]
        elif split is None:
            pass  # no splitting
        else:
            raise Exception

            # a = set(e[2] for _,e in zip(range(99999),self)) # does not scale!!!
            # a = [cat.name for cat in path.iterdir() if cat.is_dir()]
            # self._categories = sorted(set(a))

    def __iter__(self):
        for idx in range(len(self)):
            yield self.__getitem__(idx)


if __name__ == "__main__":

    def asd123asda():
        d = LibriSpeech(path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech")
        for i, s in zip(range(2), d):
            print(i, type(s[-3]))

    def asda():
        d = LibriSpeech(
            path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech",
            custom_subset=LibriSpeech.CustomSubsets.male,
        )
        for i, s in zip(range(3), d):
            print(i, s)

    def asidhja():
        samples = 6
        d_male = iter(
            LibriSpeech(
                path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech",
                custom_subset=LibriSpeech.CustomSubsets.male,
            )
        )
        d_female = iter(
            LibriSpeech(
                path=Path.home() / "Data" / "Audio" / "Speech" / "LibriSpeech",
                custom_subset=LibriSpeech.CustomSubsets.female,
            )
        )
        male_unique = {}
        while len(male_unique) < samples // 2:
            s = next(d_male)
            speaker_id = s[-3]
            if speaker_id not in male_unique:
                male_unique[speaker_id] = s

        female_unique = {}
        while len(female_unique) < samples // 2:
            s = next(d_female)
            speaker_id = s[-3]
            if speaker_id not in female_unique:
                female_unique[speaker_id] = s

        unique = (*male_unique.values(), *female_unique.values())
        assert len(unique) == samples
        print(unique, len(unique))

    # asd123asda()
    # asda()
    asidhja()
