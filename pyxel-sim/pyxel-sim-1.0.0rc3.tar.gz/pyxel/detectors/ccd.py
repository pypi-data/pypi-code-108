#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""CCD detector modeling class."""
import typing as t

from pyxel.detectors import Detector

if t.TYPE_CHECKING:
    from pyxel.detectors import CCDCharacteristics, CCDGeometry, Environment


class CCD(Detector):
    """Charge-Coupled Device class containing all detector attributes and data."""

    def __init__(
        self,
        geometry: "CCDGeometry",
        environment: "Environment",
        characteristics: "CCDCharacteristics",
    ):
        self._geometry = geometry  # type: CCDGeometry
        self._characteristics = characteristics  # type: CCDCharacteristics

        super().__init__(environment=environment)
        super().reset()

    @property
    def geometry(self) -> "CCDGeometry":
        """TBW."""
        return self._geometry

    @property
    def characteristics(self) -> "CCDCharacteristics":
        """TBW."""
        return self._characteristics
