#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 15-01-2021
           """

from typing import Sequence, Tuple

import numpy


def mask_split_speech_silence(
    vad: Sequence, data: Sequence
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    speech = []
    silence = []
    for n in range(min(len(data), len(vad))):
        if vad[n] == 1:
            speech.append(data[n])
        else:
            silence.append(data[n])

    return numpy.asarray(speech), numpy.asarray(silence)
