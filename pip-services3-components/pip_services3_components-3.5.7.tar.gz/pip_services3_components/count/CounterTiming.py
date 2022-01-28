# -*- coding: utf-8 -*-
"""
    pip_services3_components.counters.CounterTiming
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    CounterTiming implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time

from pip_services3_components.count import ICounterTimingCallback


class CounterTiming:
    """
    Callback object returned by :func:`pip_services3_components.count.ICounters.ICounters.begin_timing` to end timing
    of execution block and update the associated counter.

    Example:
        timing = counters.begin_timing("mymethod.exec_time")
        # do something
        timing.end_timing()
    """

    def __init__(self, counter: str = None, callback: ICounterTimingCallback = None):
        """
        Creates a new instance of the timing callback object.

        :param counter: an associated counter name
        :param callback: a callback that shall be called when end_timing is called.
        """

        self.__counter: str = counter
        self.__callback: ICounterTimingCallback = callback
        self.__start: float = time.perf_counter() * 1000

    def end_timing(self):
        """
        Ends timing of an execution block, calculates elapsed time and updates the associated counter.
        """

        if not (self.__callback is None):
            elapsed = time.perf_counter() * 1000 - self.__start
            self.__callback.end_timing(self.__counter, elapsed)
