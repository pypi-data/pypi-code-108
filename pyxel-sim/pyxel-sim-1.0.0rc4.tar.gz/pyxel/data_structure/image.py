#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Image class."""

from typing import TYPE_CHECKING

import numpy as np

from pyxel.data_structure import Array

if TYPE_CHECKING:
    from pyxel.detectors import Geometry


class Image(Array):
    """
    Image class defining and storing information of detector image.

    Accepted array types: ``np.uint16``, ``np.uint32``, ``np.uint64``
    """

    EXP_TYPE = np.dtype(np.uint64)
    TYPE_LIST = (
        np.dtype(np.uint16),
        np.dtype(np.uint32),
        np.dtype(np.uint64),
        np.dtype(np.float16),
        np.dtype(np.float32),
        np.dtype(np.float64),
    )

    def __init__(self, geo: "Geometry"):
        new_array = np.zeros((geo.row, geo.col), dtype=self.EXP_TYPE)

        super().__init__(new_array)
