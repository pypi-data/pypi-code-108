#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Phase-pulse processing model."""

import numpy as np

from pyxel.detectors import MKID


def convert_to_phase(
    array: np.ndarray,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> np.ndarray:
    """Convert an array of charge into phase.

    Parameters
    ----------
    array: ndarray
    wavelength: float
    responsivity: float
    scaling_factor: float

    Returns
    -------
    ndarray
    """
    if not wavelength > 0:
        raise ValueError("Only positive values accepted for wavelength.")
    if not scaling_factor > 0:
        raise ValueError("Only positive values accepted for scaling_factor.")
    if not responsivity > 0:
        raise ValueError("Only positive values accepted for responsivity.")

    output = array * wavelength * scaling_factor / responsivity
    return output.astype("float64")


def pulse_processing(
    detector: MKID,
    wavelength: float,
    responsivity: float,
    scaling_factor: float = 2.5e2,
) -> None:
    """TBW.

    Parameters
    ----------
    detector: MKID
        Pyxel :term:`MKID` detector object.
    wavelength: float
        Wavelength.
    responsivity: float
        Responsivity of the pixel.
    scaling_factor: float
        Scaling factor taking into account the missing pieces of superconducting physics,
        as well as the resonator quality factor, the bias power,
        the quasi-particle losses, etc.
    """
    if not isinstance(detector, MKID):
        raise TypeError("Expecting a MKID object for the detector.")

    detector.phase.array = convert_to_phase(
        array=detector.charge.array,
        wavelength=wavelength,
        responsivity=responsivity,
        scaling_factor=scaling_factor,
    )
