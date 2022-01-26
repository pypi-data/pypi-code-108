# -*- coding: utf-8 -*-
"""
    pip_services3_components.counters.CachedCounters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Cached counters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import datetime
import threading
import time
from abc import abstractmethod
from typing import List

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.config.IReconfigurable import IReconfigurable

from .Counter import Counter
from .CounterTiming import CounterTiming
from .CounterType import CounterType
from .ICounterTimingCallback import ICounterTimingCallback
from .ICounters import ICounters


class CachedCounters(ICounters, IReconfigurable, ICounterTimingCallback):
    """
    Abstract implementation of performance counters that measures and stores counters in memory.
    Child classes implement saving of the counters into various destinations.

    ### Configuration parameters ###
        - options:
            - interval:        interval in milliseconds to save current counters measurements (default: 5 mins)
            - reset_timeout:   timeout in milliseconds to reset the counters. 0 disables the reset (default: 0)
    """
    _default_interval = 300000

    __lock = None

    def __init__(self):
        """
        Creates a new CachedCounters object.
        """
        self._cache = {}
        self._updated = False
        self._last_dump_time = time.perf_counter()
        self._interval = self._default_interval
        self.__lock = threading.Lock()

    def get_interval(self) -> float:
        """
        Gets the counters dump/save interval.

        :return: the interval in milliseconds.
        """
        return self._interval

    def set_interval(self, value: float):
        """
        Sets the counters dump/save interval.

        :param value: a new interval in milliseconds.
        """
        self._interval = value

    @abstractmethod
    def _save(self, counters: List[Counter]):
        """
        Saves the current counters measurements.

        :param counters: current counters measurements to be saves.
        """
        raise NotImplementedError('Method from abstract implementation')

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._interval = config.get_as_float_with_default("interval", self._interval)
        self._interval = config.get_as_long_with_default("options.interval", self._interval)

    def clear(self, name: str):
        """
        Clears (resets) a counter specified by its name.

        :param name: a counter name to clear.
        """
        with self.__lock:
            del self._cache[name]

    def clear_all(self):
        """
        Clears (resets) all counters.
        """
        with self.__lock:
            self._cache = {}
            self._updated = False

    def dump(self):
        """
        Dumps (saves) the current values of counters.
        """

        if self._updated:
            messages = self.get_all()
            self._save(messages)

            with self.__lock:
                self._updated = False
                current_time = time.perf_counter() * 1000
                self._last_dump_time = current_time

    def _update(self):
        """
        Makes counter measurements as updated and dumps them when timeout expires.
        """
        with self.__lock:
            self._updated = True

        current_time = time.perf_counter() * 1000
        if current_time > self._last_dump_time + self._interval:
            try:
                self.dump()
            except:
                # Todo: decide what to do
                pass

    def get_all(self) -> List[Counter]:
        """
        Gets all captured counters.

        :return: a list with counters.
        """
        with self.__lock:
            return list(self._cache.values())

    def get(self, name: str, typ: CounterType) -> Counter:
        """
        Gets a counter specified by its name.
        It counter does not exist or its type doesn't match the specified type
        it creates a new one.

        :param name: a counter name to retrieve.

        :param typ: a counter type.

        :return: an existing or newly created counter of the specified type.
        """
        if name is None or len(name) == 0:
            raise Exception("Counter name was not set")

        with self.__lock:
            counter = self._cache[name] if name in self._cache else None

            if counter is None or counter.type != typ:
                counter = Counter(name, typ)
                self._cache[name] = counter

            return counter

    def __calculate_stats(self, counter: Counter, value: float):
        if counter is None:
            raise Exception("Missing counter")

        counter.last = value
        counter.count = counter.count + 1 if not (counter.count is None) else 1
        counter.max = max(counter.max, value) if not (counter.max is None) else value
        counter.min = min(counter.min, value) if not (counter.min is None) else value
        counter.average = (float(counter.average * (counter.count - 1)) + value) / counter.count \
            if not (counter.average is None) and counter.count > 0 else value

    def begin_timing(self, name: str) -> CounterTiming:
        """
        Begins measurement of execution time interval.
        It returns :class:`CounterTiming <pip_services3_components.count.CounterTiming.CounterTiming>` object which has to be called at
        :func:`CounterTiming.end_timing` to end the measurement and update the counter.

        :param name: a counter name of Interval type.

        :return: a :class:`CounterTiming <pip_services3_components.count.CounterTiming.CounterTiming>` callback object to end timing.
        """
        return CounterTiming(name, self)

    def end_timing(self, name: str, elapsed: float):
        """
        Ends measurement of execution elapsed time and updates specified counter.

        :param name: a counter name

        :param elapsed: execution elapsed time in milliseconds to update the counter.
        """
        counter = self.get(name, CounterType.Interval)
        self.__calculate_stats(counter, elapsed)
        self._update()

    def stats(self, name: str, value: float):
        """
        Calculates min/average/max statistics based on the current and previous values.

        :param name: a counter name of Statistics type

        :param value: a value to update statistics
        """
        counter = self.get(name, CounterType.Statistics)
        self.__calculate_stats(counter, value)
        self._update()

    def last(self, name: str, value: float):
        """
        Records the last calculated measurement value.
        Usually this method is used by metrics calculated externally.

        :param name: a counter name of Last type.

        :param value: a last value to record.
        """
        counter = self.get(name, CounterType.LastValue)
        counter.last = value
        self._update()

    def timestamp_now(self, name: str):
        """
        Records the current time as a timestamp.

        :param name: a counter name of Timestamp type.
        """
        self.timestamp(name, datetime.datetime.utcnow())

    def timestamp(self, name: str, value: datetime.datetime):
        """
        Records the given timestamp.

        :param name: a counter name of Timestamp type.

        :param value: a timestamp to record.
        """
        counter = self.get(name, CounterType.Timestamp)
        counter.time = value if not (value is None) else datetime.datetime.utcnow()
        self._update()

    def increment_one(self, name: str):
        """
        Increments counter by 1.

        :param name: a counter name of Increment type.
        """
        self.increment(name, 1)

    def increment(self, name: str, value: float):
        """
        Increments counter by given value.

        :param name: a counter name of Increment type.

        :param value: a value to add to the counter.
        """
        counter = self.get(name, CounterType.Increment)
        counter.count = value if counter.count is None else counter.count + value
        self._update()
