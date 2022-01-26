#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""

import typing as t

import numpy as np

from pyxel import load_table
from pyxel.evaluator import eval_range


class Readout:
    """TBW.

    Parameters
    ----------
    times
    times_from_file
    start_time
    non_destructive
    """

    def __init__(
        self,
        times: t.Optional[t.Union[t.Sequence, str]] = None,
        times_from_file: t.Optional[str] = None,
        start_time: float = 0.0,
        non_destructive: bool = False,
    ):
        self._time_domain_simulation = True

        if times is not None and times_from_file is not None:
            raise ValueError("Both times and times_from_file specified. Choose one.")
        elif times is None and times_from_file is None:
            self._times = np.array(
                [1]
            )  # by convention default readout/exposure time is 1 second
            self._time_domain_simulation = False
        elif times_from_file:
            self._times = load_table(times_from_file).to_numpy(dtype=float).flatten()
        elif times:
            self._times = np.array(eval_range(times), dtype=float)
        else:
            raise ValueError("Sampling times not specified.")

        if self._times[0] == 0:
            raise ValueError("Readout times should be non-zero values.")
        elif start_time == self._times[0]:
            raise ValueError("Readout times should be greater than start time.")

        self._non_destructive = non_destructive

        self._times_linear = True  # type: bool
        self._start_time = start_time  # type:float
        self._steps = np.array([])  # type: np.ndarray
        self._num_steps = 0  # type: int
        self._set_steps()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<num_steps={self._num_steps}>"

    def _set_steps(self) -> None:
        """TBW."""
        self._times, self._steps = calculate_steps(self._times, self._start_time)
        self._times_linear = bool(np.all(self._steps == self._steps[0]))
        self._num_steps = len(self._times)

    def time_step_it(self) -> t.Iterator[t.Tuple[float, float]]:
        """TBW."""
        return zip(self._times, self._steps)

    @property
    def times(self) -> t.Any:
        """TBW."""
        return self._times

    @property
    def time_domain_simulation(self) -> bool:
        """TBW."""
        return self._time_domain_simulation

    @property
    def steps(self) -> np.ndarray:
        """TBW."""
        return self._steps

    @property
    def non_destructive(self) -> bool:
        """TBW."""
        return self._non_destructive


def calculate_steps(
    times: np.ndarray, start_time: float
) -> t.Tuple[np.ndarray, np.ndarray]:
    """Calculate time differences for a given array and start time.

    Parameters
    ----------
    times: ndarray
    start_time: float

    Returns
    -------
    times: ndarray
        Modified times according to start time.
    steps: ndarray
        Steps corresponding to times.
    """
    steps = np.diff(
        np.concatenate((np.array([start_time]), times), axis=0),
        axis=0,
    )

    return times, steps
