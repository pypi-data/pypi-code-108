# -*- coding: utf-8 -*-
"""
    tests.count.CountersFixture
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time

from pip_services3_components.count import CounterType


class CountersFixture:
    _counters = None

    def __init__(self, counters):
        self._counters = counters

    def test_simple_counters(self):
        self._counters.last("Test.LastValue", 123)
        self._counters.last("Test.LastValue", 123456)

        counter = self._counters.get("Test.LastValue", CounterType.LastValue)
        assert counter is not None
        assert abs(counter.last - 123456) < 0.001

        self._counters.increment_one("Test.Increment")
        self._counters.increment("Test.Increment", 3)

        counter = self._counters.get("Test.Increment", CounterType.Increment)
        assert counter is not None
        assert counter.count == 4

        self._counters.timestamp_now("Test.Timestamp")
        self._counters.timestamp_now("Test.Timestamp")

        counter = self._counters.get("Test.Timestamp", CounterType.Timestamp)
        assert counter is not None
        assert counter.time is not None

        self._counters.stats("Test.Statistics", 1)
        self._counters.stats("Test.Statistics", 2)
        self._counters.stats("Test.Statistics", 3)

        counter = self._counters.get("Test.Statistics", CounterType.Statistics)
        assert counter is not None

        assert abs(counter.average - 2) < 0.001

        self._counters.dump()

    def test_measure_elapsed_time(self):
        timing = self._counters.begin_timing("Test.Elapsed")
        try:
            time.sleep(0.1)
        finally:
            timing.end_timing()

        counter = self._counters.get("Test.Elapsed", CounterType.Interval)
        assert counter is not None
        # Something is wrong with timing
        assert counter.last > 50
        assert counter.last < 5000

        self._counters.dump()
