# -*- coding: utf-8 -*-
import time

from pip_services3_components.count import CachedCounters, CounterType


class CountersFixture:
    _counters: CachedCounters

    def __init__(self, counters: CachedCounters):
        self._counters = counters

    def test_simple_counters(self):
        self._counters.last("Test.LastValue", 123)
        self._counters.last("Test.LastValue", 123456)

        counter = self._counters.get("Test.LastValue", CounterType.LastValue)
        assert counter is not None
        assert counter.last is not None
        assert counter.last == 123456, 3

        self._counters.increment_one('Test.Increment')
        self._counters.increment('Test.Increment', 3)

        counter = self._counters.get('Test.Increment', CounterType.Increment)
        assert counter is not None
        assert counter.count == 4

        self._counters.timestamp_now('Test.Timestamp')
        self._counters.timestamp_now('Test.Timestamp')

        counter = self._counters.get('Test.Timestamp', CounterType.Timestamp)
        assert counter is not None
        assert counter.time is not None

        self._counters.stats('Test.Statistics', 1)
        self._counters.stats('Test.Statistics', 2)
        self._counters.stats('Test.Statistics', 3)

        counter = self._counters.get('Test.Statistics', CounterType.Statistics)
        assert counter is not None
        assert counter.average == 2, 3

        self._counters.dump()

        # time.sleep(1)

    def test_measure_elapsed_time(self):
        timer = self._counters.begin_timing('Test.Elapsed')

        time.sleep(0.1)

        timer.end_timing()

        counter = self._counters.get('Test.Elapsed', CounterType.Interval)
        assert counter.last > 50
        assert counter.last < 5000

        self._counters.dump()

        # time.sleep(1)
