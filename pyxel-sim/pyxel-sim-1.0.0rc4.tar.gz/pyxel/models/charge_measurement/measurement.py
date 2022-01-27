#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Charge readout model."""

import typing as t

import numpy as np

from pyxel.detectors import Detector


def apply_gain(pixel_2d: np.ndarray, gain: float) -> np.ndarray:
    """Apply a gain (in V/e-) to a pixel array (in e-).

    Parameters
    ----------
    pixel_2d : ndarray
        2D array of pixels. Unit: e-
    gain : float
        Gain to apply. Unit: V/e-

    Returns
    -------
    ndarray
        2D array of signals. Unit: V
    """
    new_data_2d = pixel_2d * gain

    return new_data_2d


def simple_measurement(detector: Detector, gain: t.Optional[float] = None) -> None:
    """Convert the pixel array into signal array.

    Notes
    -----
    If no gain is provided, then its value will be the sensitivity of charge readout
    provided in the ``Detector`` object.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    gain : float, optional.
        Gain to apply. By default, this is the sensitivity of charge readout. Unit: V/e-
    """
    if gain is None:
        char = detector.characteristics
        gain = char.charge_to_volt_conversion

    # Compute
    signal_2d = apply_gain(pixel_2d=detector.pixel.array, gain=gain)

    detector.signal.array = signal_2d.astype("float64")
