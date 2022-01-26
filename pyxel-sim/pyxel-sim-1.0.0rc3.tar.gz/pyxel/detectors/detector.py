#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Detector class."""
import collections
import typing as t
from pathlib import Path

import h5py as h5
import numpy as np

from pyxel import __version__
from pyxel.data_structure import (
    Charge,
    Image,
    Persistence,
    Photon,
    Pixel,
    Signal,
    SimplePersistence,
)
from pyxel.detectors import Environment
from pyxel.detectors.readout_properties import ReadoutProperties
from pyxel.util.memory import get_size, memory_usage_details

__all__ = ["Detector"]


# TODO: Add methods to save/load a `Detector` instance to the filesystem. See #329
class Detector:
    """The detector class."""

    def __init__(self, environment: Environment):
        self.environment = environment  # type: Environment

        self.header = collections.OrderedDict()  # type: t.Dict[str, object]

        self._photon = None  # type: t.Optional[Photon]
        self._charge = None  # type: t.Optional[Charge]
        self._pixel = None  # type: t.Optional[Pixel]
        self._signal = None  # type: t.Optional[Signal]
        self._image = None  # type: t.Optional[Image]

        # This will be the memory of the detector where trapped charges will be saved
        self._memory = dict()  # type: t.Dict
        self._persistence = (
            None
        )  # type: t.Optional[t.Union[Persistence, SimplePersistence]]

        self.input_image = None  # type: t.Optional[np.ndarray]
        self._output_dir = None  # type: t.Optional[Path]  # TODO: See #330

        self._readout_properties = None  # type: t.Optional["ReadoutProperties"]

        self._numbytes = get_size(self)

    @property
    def geometry(self):
        """TBW."""
        raise NotImplementedError

    @property
    def characteristics(self):
        """TBW."""
        raise NotImplementedError

    @property
    def photon(self) -> Photon:
        """TBW."""
        if not self._photon:
            raise RuntimeError("Photon array is not initialized ! ")
        return self._photon

    @photon.setter
    def photon(self, obj: Photon) -> None:
        self._photon = obj

    @property
    def charge(self) -> Charge:
        """TBW."""
        if not self._charge:
            raise RuntimeError("'charge' not initialized.")

        return self._charge

    @property
    def pixel(self) -> Pixel:
        """TBW."""
        if not self._pixel:
            raise RuntimeError("'pixel' not initialized.")

        return self._pixel

    @property
    def signal(self) -> Signal:
        """TBW."""
        if not self._signal:
            raise RuntimeError("'signal' not initialized.")

        return self._signal

    @property
    def image(self) -> Image:
        """TBW."""
        if not self._image:
            raise RuntimeError("'image' not initialized.")

        return self._image

    def reset(self) -> None:
        """TBW."""
        self._photon = Photon(geo=self.geometry)
        self._charge = Charge(geo=self.geometry)
        self._pixel = Pixel(geo=self.geometry)
        self._signal = Signal(geo=self.geometry)
        self._image = Image(geo=self.geometry)

    def empty(self, empty_all: bool = True) -> None:
        """Empty the data in the detector.

        Returns
        -------
        None
        """
        if self._photon:
            self.photon.array *= 0
        if empty_all:
            if self._charge:
                self._charge.empty()
            if self._pixel:
                self.pixel.array *= 0
            if self._signal:
                self.signal.array *= 0
            if self._image:
                self.image.array *= 0

    # TODO: Set an `Output` object ? Is it really needed ? See #330
    def set_output_dir(self, path: t.Union[str, Path]) -> None:
        """Set output directory path."""
        self._output_dir = Path(path)

    # TODO: Set an `Output` object ? Is it really needed ? See #330
    @property
    def output_dir(self) -> Path:
        """Output directory path."""
        if self._output_dir is None:
            raise RuntimeError("'output_dir' is not initialized.")

        return self._output_dir

    def set_readout(
        self,
        num_steps: int,
        start_time: float,
        end_time: float,
        ndreadout: bool = False,
        times_linear: bool = True,
    ) -> None:
        """Set readout."""
        self._readout_properties = ReadoutProperties(
            num_steps=num_steps,
            start_time=start_time,
            end_time=end_time,
            ndreadout=ndreadout,
            times_linear=times_linear,
        )

    @property
    def time(self) -> float:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.time
        else:
            raise ValueError("No readout defined.")

    @time.setter
    def time(self, value: float) -> None:
        """TBW."""
        if self._readout_properties is not None:
            self._readout_properties.time = value
        else:
            raise ValueError("No readout defined.")

    @property
    def start_time(self) -> float:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.start_time
        else:
            raise ValueError("No readout defined.")

    @start_time.setter
    def start_time(self, value: float) -> None:
        """TBW."""
        if self._readout_properties is not None:
            self._readout_properties.start_time = value
        else:
            raise ValueError("No readout defined.")

    @property
    def absolute_time(self) -> float:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.absolute_time
        else:
            raise ValueError("No readout defined.")

    @property
    def time_step(self) -> float:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.time_step
        else:
            raise ValueError("No readout defined.")

    @time_step.setter
    def time_step(self, value: float) -> None:
        """TBW."""
        if self._readout_properties is not None:
            self._readout_properties.time_step = value
        else:
            raise ValueError("No readout defined.")

    @property
    def times_linear(self) -> bool:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.times_linear
        else:
            raise ValueError("No readout defined.")

    @property
    def num_steps(self) -> int:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.num_steps
        else:
            raise ValueError("No readout defined.")

    @property
    def pipeline_count(self) -> float:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.pipeline_count
        else:
            raise ValueError("No readout defined.")

    @pipeline_count.setter
    def pipeline_count(self, value: int) -> None:
        """TBW."""
        if self._readout_properties is not None:
            self._readout_properties.pipeline_count = value
        else:
            raise ValueError("No readout defined.")

    @property
    def read_out(self) -> bool:
        """TBW."""
        if self._readout_properties is not None:
            return self._readout_properties.read_out
        else:
            raise ValueError("No readout defined.")

    @read_out.setter
    def read_out(self, value: bool) -> None:
        """TBW."""
        if self._readout_properties is not None:
            self._readout_properties.read_out = value
        else:
            raise ValueError("No readout defined.")

    @property
    def is_dynamic(self) -> bool:
        """Return if detector is dynamic (time dependent) or not.

        By default it is not dynamic.
        """
        if self._readout_properties is not None:
            return True
        else:
            return False

    @property
    def non_destructive_readout(self) -> bool:
        """Return if detector readout mode is destructive or integrating.

        By default it is destructive (non-integrating).
        """
        if self._readout_properties is not None:
            return self._readout_properties.non_destructive
        else:
            raise ValueError("No sampling defined.")

    def has_persistence(self) -> bool:
        """TBW."""
        if self._persistence is not None:
            return True
        else:
            return False

    @property
    def persistence(self) -> t.Union[Persistence, SimplePersistence]:
        """TBW."""
        if self._persistence is not None:
            return self._persistence
        else:
            raise RuntimeError("'persistence' not initialized.")

    @persistence.setter
    def persistence(self, value: t.Union[Persistence, SimplePersistence]) -> None:
        """TBW."""
        if not isinstance(value, (Persistence, SimplePersistence)):
            raise TypeError(
                "Expecting Persistence or SimplePersistence type to set detector persistence."
            )
        self._persistence = value

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
                    self.charge.frame,
                ],
                ["Signal", "Image", "Photon", "Pixel", "Charge"],
            ):
                dataset = detector_grp.create_dataset(name, shape=np.shape(array))
                dataset[:] = array
