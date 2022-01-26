# -*- coding: utf-8 -*-
import os

from pip_services3_commons.config import ConfigParams

from pip_services3_datadog.count.DataDogCounters import DataDogCounters
from test.fixtures.CountersFixture import CountersFixture


class TestDataDogCounters:
    _counters: DataDogCounters
    _fixture: CountersFixture

    def setup_method(self):
        api_key = os.environ.get('DATADOG_API_KEY') or '3eb3355caf628d4689a72084425177ac'

        self._counters = DataDogCounters()
        self._fixture = CountersFixture(self._counters)

        config = ConfigParams.from_tuples(
            'source', 'test',
            'credential.access_key', api_key
        )

        self._counters.configure(config)

        self._counters.open(None)

    def teardown_method(self):
        self._counters.close(None)

    def test_simple_counters(self):
        self._fixture.test_simple_counters()

    def test_measure_elapsed_time(self):
        self._fixture.test_measure_elapsed_time()
