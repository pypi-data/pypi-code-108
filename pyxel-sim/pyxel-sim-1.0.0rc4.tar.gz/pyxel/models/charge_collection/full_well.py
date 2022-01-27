#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel full well models."""
import typing as t

import numpy as np

from pyxel.detectors import Detector


def apply_simple_full_well_capacity(array: np.ndarray, fwc: int) -> np.ndarray:
    """Apply full well capacity to an array.

    Parameters
    ----------
    array: ndarray
    fwc: int

    Returns
    -------
    output: ndarray
    """
    array[array > fwc] = fwc
    return array


def simple_full_well(detector: Detector, fwc: t.Optional[int] = None) -> None:
    """Limit the amount of charge in pixel due to full well capacity.

    Uses full well capacity in the characteristics of the detector object if not overridden by the function argument.

    Parameters
    ----------
    detector: Detector
    fwc: int
    """
    if fwc is None:
        fwc_input = detector.characteristics.full_well_capacity
    else:
        fwc_input = fwc

    if fwc_input < 0:
        raise ValueError("Full well capacity should be a positive number.")

    charge_array = apply_simple_full_well_capacity(
        array=detector.pixel.array, fwc=fwc_input
    )

    detector.pixel.array = charge_array
