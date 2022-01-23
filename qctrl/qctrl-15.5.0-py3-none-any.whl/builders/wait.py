# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import logging
import time
from bisect import bisect
from collections import namedtuple
from typing import List

LOGGER = logging.getLogger(__name__)


class Wait:  # pylint:disable=too-few-public-methods
    """Class that can be used to sleep the program differing amounts of time
    based on ranges. Range must start at 0 and must be specified in ascending
    order.
    """

    Interval = namedtuple("Interval", ["frequency", "start"])
    default_intervals = [
        Interval(frequency=2, start=0),
        Interval(frequency=5, start=60 * 2),
        Interval(frequency=10, start=60 * 10),
    ]

    def __init__(self, intervals: List[Interval] = None):
        self._elapsed_time = 0
        self._intervals, self._frequency = self._build(
            intervals or self.default_intervals
        )

    @staticmethod
    def _build(intervals: List[Interval]):

        _frequency, _intervals = zip(*intervals)

        if any(val < 0 for val in _frequency):
            raise ValueError("Frequency values cannot be negative.")

        if any(val < 0 for val in _intervals):
            raise ValueError("Interval range values cannot be negative.")

        if any(_intervals[i] > _intervals[i + 1] for i in range(len(_intervals) - 1)):
            raise ValueError("Interval ranges need to be ascending.")

        # builds an updated frequency list to be used with bisection
        _frequency_list = [_frequency[0], *list(_frequency), _frequency[-1]]
        return _intervals, _frequency_list

    def _get_frequency(self, value: int):
        """
        Uses bisection to retrieve the frequency.
        """
        num = bisect(self._intervals, value)
        return self._frequency[num]

    def __call__(self):
        _current_frequency = self._get_frequency(self._elapsed_time)
        LOGGER.debug("Sleeping for %s", _current_frequency)
        time.sleep(_current_frequency)
        self._elapsed_time += _current_frequency
