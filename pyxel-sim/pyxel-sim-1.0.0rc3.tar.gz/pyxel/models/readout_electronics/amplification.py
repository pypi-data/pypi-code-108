#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout electronics model."""

import numpy as np

from pyxel.detectors import Detector


def apply_amplify(
    signal_2d: np.ndarray,
    amplifier_gain: float,
) -> np.ndarray:
    """Apply gain from the output amplifier and signal processor.

    Parameters
    ----------
    signal_2d : ndarray
        2D signal to amplify. Unit: V
    amplifier_gain : float
        Gain of amplifier. Unit: V/V

    Returns
    -------
    ndarray
        2D amplified signal. Unit: V
    """
    amplified_signal_2d = signal_2d * amplifier_gain

    return amplified_signal_2d


def simple_amplifier(detector: Detector) -> None:
    """Amplify signal using gain from the output amplifier and the signal processor.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    """
    char = detector.characteristics

    amplified_signal_2d = apply_amplify(
        signal_2d=detector.signal.array,
        amplifier_gain=char.pre_amplification,
    )  # type: np.ndarray

    detector.signal.array = amplified_signal_2d
