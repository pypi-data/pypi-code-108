# -*- coding: utf-8 -*-
"""
    tests.logs.test_LogCounters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer import Descriptor
from pip_services3_commons.refer import References

from pip_services3_components.count import LogCounters
from pip_services3_components.log import NullLogger
from .CountersFixture import CountersFixture


class TestLogCounters:

    counters: LogCounters = None
    fixture = None

    def setup_method(self, method):
        log = NullLogger()
        refs = References.from_tuples(
            Descriptor("pip-services", "logger", "null", "default", "1.0"), log
        )

        self.counters = LogCounters()
        self.counters.set_references(refs)

        self.fixture = CountersFixture(self.counters)

    def test_simple_counters(self):
        self.fixture.test_simple_counters()

    def test_measure_elapsed_time(self):
        self.fixture.test_measure_elapsed_time()
