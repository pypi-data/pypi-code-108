#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel charge collection model."""

from pyxel.detectors import Detector


def simple_collection(detector: Detector) -> None:
    """Associate charge with the closest pixel.

    Parameters
    ----------
    detector: Detector
        Pyxel Detector object.
    """
    detector.pixel.array += detector.charge.array
