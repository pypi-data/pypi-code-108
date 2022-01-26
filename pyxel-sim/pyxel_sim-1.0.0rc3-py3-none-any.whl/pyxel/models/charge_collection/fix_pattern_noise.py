#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fix pattern noise model."""

import typing as t
from pathlib import Path

import numpy as np
from typing_extensions import Literal

from pyxel.detectors import Detector, Geometry
from pyxel.util import load_cropped_and_aligned_image


def fix_pattern_noise(
    detector: Detector,
    filename: t.Union[str, Path],
    position: t.Tuple[int, int] = (0, 0),
    align: t.Optional[
        Literal["center", "top_left", "top_right", "bottom_left", "bottom_right"]
    ] = None,
) -> None:
    """Add fix pattern noise caused by pixel non-uniformity during charge collection.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    filename : str or Path
        Path to a file with an array or an image.
    position: tuple
        Indices of starting row and column, used when fitting noise to detector.
    align: Literal
        Keyword to align the noise to detector. Can be any from:
        ("center", "top_left", "top_right", "bottom_left", "bottom_right")
    """
    geo = detector.geometry  # type: Geometry
    position_y, position_x = position

    # Load charge profile as numpy array.
    pnu_2d = load_cropped_and_aligned_image(
        shape=(geo.row, geo.col),
        filename=filename,
        position_x=position_x,
        position_y=position_y,
        align=align,
    )  # type: np.ndarray

    detector.pixel.array *= pnu_2d
