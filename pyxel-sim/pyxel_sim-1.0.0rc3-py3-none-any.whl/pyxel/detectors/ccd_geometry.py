#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
from pyxel.detectors import Geometry


class CCDGeometry(Geometry):
    """Geometrical attributes of a :term:`CCD` detector.

    Parameters
    ----------
    row: int
        Number of pixel rows.
    col: int
        Number of pixel columns.
    total_thickness: float
        Thickness of detector. Unit: um
    pixel_vert_size: float
        Vertical dimension of pixel. Unit: um
    pixel_horz_size: float
        Horizontal dimension of pixel. Unit: um
    """
