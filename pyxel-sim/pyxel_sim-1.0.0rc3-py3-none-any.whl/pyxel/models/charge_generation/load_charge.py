#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to load charge profiles."""

import typing as t
from pathlib import Path

import numpy as np
from typing_extensions import Literal

from pyxel.detectors import Detector, Geometry
from pyxel.util import load_cropped_and_aligned_image


def load_charge(
    detector: Detector,
    filename: t.Union[str, Path],
    position: t.Tuple[int, int] = (0, 0),
    align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
    time_scale: float = 1.0,
) -> None:
    """Load charge from txt file for detector, mostly for but not limited to :term:`CCDs<CCD>`.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        File path.
    position: tuple
        Indices of starting row and column, used when fitting charge to detector.
    align: Literal
        Keyword to align the charge to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    time_scale: float
        Time scale of the input charge, default is 1 second. 0.001 would be ms.
    """
    geo = detector.geometry  # type: Geometry
    position_y, position_x = position

    # Load charge profile as numpy array.
    charges = load_cropped_and_aligned_image(
        shape=(geo.row, geo.col),
        filename=filename,
        position_x=position_x,
        position_y=position_y,
        align=align,
    )  # type: np.ndarray

    charges *= detector.time_step / time_scale

    # Add charges in 'detector'
    detector.charge.add_charge_array(charges)
