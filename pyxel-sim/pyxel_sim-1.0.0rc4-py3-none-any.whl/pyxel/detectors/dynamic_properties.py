#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Sampling detector properties class."""


class DynamicProperties:
    """Sampling detector properties."""

    def __init__(
        self,
        num_steps: int,
        start_time: float = 0.0,
        end_time: float = 0.0,
        ndreadout: bool = False,
        times_linear: bool = True,
    ):
        """Create an instance of DynamicProperties.

        Parameters
        ----------
        num_steps
        start_time
        end_time
        ndreadout
        times_linear
        """
        # Fixed at beginning
        self._num_steps = num_steps  # type: int
        self._start_time = start_time  # type: float
        self._end_time = end_time  # type: float
        self._non_destructive = ndreadout  # type: bool
        self._times_linear = times_linear  # type: bool

        # Changing
        self._time = 0.0  # type: float
        self._time_step = 0.0  # type: float
        self._read_out = True  # type: bool
        self._pipeline_count = 0  # type: int

    @property
    def num_steps(self) -> int:
        """TBW."""
        return self._num_steps

    @property
    def start_time(self) -> float:
        """TBW."""
        return self._end_time

    @property
    def end_time(self) -> float:
        """TBW."""
        return self._end_time

    @property
    def non_destructive_readout(self) -> bool:
        """TBW."""
        return self._non_destructive

    @property
    def times_linear(self) -> bool:
        """TBW."""
        return self._times_linear

    @property
    def time(self) -> float:
        """TBW."""
        return self._time

    @time.setter
    def time(self, value: float) -> None:
        """TBW."""
        self._time = value

    @property
    def time_step(self) -> float:
        """TBW."""
        return self._time_step

    @time_step.setter
    def time_step(self, value: float) -> None:
        """TBW."""
        self._time_step = value

    @property
    def read_out(self) -> bool:
        """TBW."""
        return self._read_out

    @read_out.setter
    def read_out(self, value: bool) -> None:
        """TBW."""
        self._read_out = value

    @property
    def pipeline_count(self) -> float:
        """TBW."""
        return self._pipeline_count

    @pipeline_count.setter
    def pipeline_count(self, value: int) -> None:
        """TBW."""
        self._pipeline_count = value
