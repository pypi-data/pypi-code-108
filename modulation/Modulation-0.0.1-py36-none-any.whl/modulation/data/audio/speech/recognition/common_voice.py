#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 03-12-2020
           """

import torch
import torchaudio
from torchaudio.datasets import COMMONVOICE


class CommonVoice(COMMONVOICE):
    def __init__(self, root: str, n_threads=0):
        super().__init__(root, download=False)
        yesno_data = torchaudio.datasets.COMMONVOICE("", download=True)
        data_loader = torch.utils.data.DataLoader(
            yesno_data, batch_size=1, shuffle=True, num_workers=n_threads
        )
