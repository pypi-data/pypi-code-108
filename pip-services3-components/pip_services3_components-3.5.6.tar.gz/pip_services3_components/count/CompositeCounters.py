# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.CompositeCounters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Composite counters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime
from typing import List

from pip_services3_commons.refer import IReferences
from pip_services3_commons.refer.Descriptor import Descriptor
from pip_services3_commons.refer.IReferenceable import IReferenceable

from .CounterTiming import CounterTiming
from .ICounterTimingCallback import ICounterTimingCallback
from .ICounters import ICounters


class CompositeCounters(ICounters, ICounterTimingCallback, IReferenceable):
    """
    Aggregates all counters from component references under a single component.

    It allows to capture metrics and conveniently send them to multiple destinations.

    ### References ###
        - `*:counters:*:*:1.0`     (optional) ICounters components to pass collected measurements

    Example:

    .. code-block:: python

        class MyComponent(IReferenceable):
            _counters = CompositeCounters()

        def set_references(self, references):
            self._counters.set_references(references)

        def my_method(self):
            self._counters.increment("mycomponent.mymethod.calls")
            timing = this._counters.begin_timing("mycomponent.mymethod.exec_time")
            # do something

            timing.end_timing()
    """
    _counters: List[ICounters] = []

    def __init__(self, references: IReferences = None):
        """
        Creates a new instance of the counters.

        :param references: references to locate the component dependencies.
        """

        if not (references is None):
            self.set_references(references)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        descriptor = Descriptor(None, "counters", None, None, None)
        counters = references.get_optional(descriptor)
        for counter in counters:
            if isinstance(counter, ICounters):
                self._counters.append(counter)

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

        See :func:`CounterTiming.end_timing`
        """
        for counter in self._counters:
            if isinstance(counter, ICounterTimingCallback):
                counter.end_timing(name, elapsed)

    def stats(self, name: str, value: float):
        """
        Calculates min/average/max statistics based on the current and previous values.

        :param name: a counter name of Statistics type

        :param value: a value to update statistics
        """
        for counter in self._counters:
            counter.stats(name, value)

    def last(self, name: str, value: float):
        """
        Records the last calculated measurement value.
        Usually this method is used by metrics calculated externally.

        :param name: a counter name of Last type.

        :param value: a last value to record.
        """
        for counter in self._counters:
            counter.last(name, value)

    def timestamp_now(self, name: str):
        """
        Records the current time as a timestamp.

        :param name: a counter name of Timestamp type.
        """
        for counter in self._counters:
            counter.timestamp_now(name)

    def timestamp(self, name: str, value: datetime.datetime):
        """
        Records the given timestamp.

        :param name: a counter name of Timestamp type.

        :param value: a timestamp to record.
        """
        for counter in self._counters:
            counter.timestamp(name, value)

    def increment_one(self, name: str):
        """
        Increments counter by 1.

        :param name: a counter name of Increment type.
        """
        for counter in self._counters:
            counter.increment_one(name)

    def increment(self, name: str, value: float):
        """
        Increments counter by given value.

        :param name: a counter name of Increment type.

        :param value: a value to add to the counter.
        """
        for counter in self._counters:
            counter.increment(name, value)
