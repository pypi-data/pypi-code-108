#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Pixel class."""

from typing import TYPE_CHECKING

import numpy as np

from pyxel.data_structure import Array

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Pixel(Array):
    """Pixel class defining and storing information of charge packets within pixel.

    Accepted array types: ``np.int32``, ``np.int64``, ``np.uint32``, ``np.uint64``,
    ``np.float16``, ``np.float32``, ``np.float64``.
    """

    EXP_TYPE = float
    TYPE_LIST = (
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )

    def __init__(self, geo: "Geometry"):
        new_array = np.zeros((geo.row, geo.col), dtype=self.EXP_TYPE)

        super().__init__(new_array)
