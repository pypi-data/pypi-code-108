#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel charge injection functions for CCDs."""
import typing as t

import numpy as np

from pyxel.detectors import CCD


def compute_charge_blocks(
    output_shape: t.Tuple[int, int],
    charge_level: float,
    block_start: int = 0,
    block_end: t.Optional[int] = None,
) -> np.ndarray:
    """Compute a block of charges to be injected in the detector.

    Parameters
    ----------
    output_shape: tuple
        Output shape of the array.
    charge_level: int
        Value of charges.
    block_start: int
        Starting row of the injected charge.
    block_end: int
        Ending row for the injected charge.

    Returns
    -------
    charge: ndarray
    """
    if block_end is None:
        block_end = output_shape[0]  # number of rows

    # all pixels has zero charge by default
    charge = np.zeros((output_shape[0], output_shape[1]))
    charge[slice(block_start, block_end), :] = charge_level

    return charge


def charge_blocks(
    detector: CCD,
    charge_level: float,
    block_start: int = 0,
    block_end: t.Optional[int] = None,
) -> None:
    """Inject a block of charge into the :term:`CCD` detector.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    charge_level: int
        Value of charges.
    block_start: int
        Starting row of the injected charge.
    block_end: int
        Ending row for the injected charge.
    """
    if not isinstance(detector, CCD):
        raise TypeError("Expecting a CCD object for detector.")
    if charge_level < 0:
        raise ValueError("Charge level value should not be a negative number.")

    shape = (detector.geometry.row, detector.geometry.col)

    if not 0 <= block_start <= shape[0]:
        raise ValueError("Block start not in range of the detector shape.")
    if block_end and not 0 <= block_end <= shape[0]:
        raise ValueError("Block end not in range of the detector shape.")

    charge = compute_charge_blocks(
        output_shape=shape,
        charge_level=charge_level,
        block_start=block_start,
        block_end=block_end,
    )

    detector.charge.add_charge_array(charge)
