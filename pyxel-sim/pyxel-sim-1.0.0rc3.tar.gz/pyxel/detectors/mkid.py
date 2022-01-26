#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

""":term:`MKID`-array detector modeling class."""

import typing as t
from pathlib import Path

import h5py as h5
import numpy as np

from pyxel import __version__
from pyxel.data_structure import Phase
from pyxel.detectors import Detector
from pyxel.util.memory import memory_usage_details

if t.TYPE_CHECKING:
    from pyxel.detectors import Environment, MKIDCharacteristics, MKIDGeometry


class MKID(Detector):
    """:term:`MKID`-based detector class containing all detector attributes and data."""

    def __init__(
        self,
        geometry: "MKIDGeometry",
        environment: "Environment",
        characteristics: "MKIDCharacteristics",
    ):
        self._geometry = geometry  # type: MKIDGeometry
        self._characteristics = characteristics  # type: MKIDCharacteristics
        self._phase = None  # type: t.Optional[Phase]

        super().__init__(environment=environment)
        self.reset()

    def reset(self) -> None:
        """TBW."""
        super().reset()
        self._phase = Phase(geo=self.geometry)

    def empty(self, empty_all: bool = True) -> None:
        """Empty the data in the detector.

        Returns
        -------
        None
        """
        super().empty(empty_all)

        if empty_all and self._phase:
            self.phase.array *= 0

    @property
    def geometry(self) -> "MKIDGeometry":
        """TBW."""
        return self._geometry

    @property
    def characteristics(self) -> "MKIDCharacteristics":
        """TBW."""
        return self._characteristics

    @property
    def phase(self) -> Phase:
        """TBW."""
        if not self._phase:
            raise RuntimeError("'phase' not initialized.")

        return self._phase

    def memory_usage(
        self, print_result: bool = True, human_readable: bool = True
    ) -> dict:
        """TBW.

        Returns
        -------
        dict
            Dictionary of attribute memory usage
        """
        attributes = [
            "_photon",
            "_charge",
            "_pixel",
            "_signal",
            "_image",
            "_phase",
            "material",
            "environment",
            "_geometry",
            "_characteristics",
        ]

        return memory_usage_details(
            self, attributes, print_result=print_result, human_readable=human_readable
        )

    # TODO: Move this to another place. See #241
    def to_hdf5(self, filename: t.Union[str, Path]) -> None:
        """Convert the detector to a HDF5 object."""
        with h5.File(filename, "w") as h5file:
            h5file.attrs["type"] = self.__class__.__name__
            h5file.attrs["pyxel-version"] = str(__version__)
            detector_grp = h5file.create_group("detector")
            for array, name in zip(
                [
                    self.signal.array,
                    self.image.array,
                    self.photon.array,
                    self.pixel.array,
                    self.phase.array,
                    self.charge.frame,
                ],
                ["Signal", "Image", "Photon", "Pixel", "Phase", "Charge"],
            ):
                dataset = detector_grp.create_dataset(name, shape=np.shape(array))
                dataset[:] = array
