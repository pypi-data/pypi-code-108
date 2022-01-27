#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import typing as t
from pyxel.util.memory import get_size


class Environment:
    """Environmental attributes of the detector.

    Parameters
    ----------
    temperature: float, optional
        Temperature of the detector. Unit: K
    """

    def __init__(self, temperature: t.Optional[float] = None):
        if temperature and not (0.0 <= temperature <= 1000.0):
            raise ValueError("'temperature' must be between 0.0 and 1000.0.")

        self._temperature = temperature

        self._numbytes = 0

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}(temperature={self._temperature!r})"

    @property
    def temperature(self) -> float:
        """Get Temperature of the detector."""
        if self._temperature:
            return self._temperature
        else:
            raise ValueError("'temperature' not specified in detector environment.")

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set Temperature of the detector."""
        if not (0.0 <= value <= 1000.0):
            raise ValueError("'temperature' must be between 0.0 and 1000.0.")

        self._temperature = value

    @property
    def numbytes(self) -> int:
        """Recursively calculates object size in bytes using Pympler library.

        Returns
        -------
        int
            Size of the object in bytes.
        """
        self._numbytes = get_size(self)
        return self._numbytes
