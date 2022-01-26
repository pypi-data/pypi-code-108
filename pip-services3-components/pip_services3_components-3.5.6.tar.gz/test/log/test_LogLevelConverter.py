# -*- coding: utf-8 -*-
"""
    tests.log.test_LogLevelConverter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_components.log import LogLevel
from pip_services3_components.log import LogLevelConverter


class TestLogLevel:

    def test_to_log_level(self):
        assert LogLevelConverter.to_log_level("1") == LogLevel.Fatal
        assert LogLevelConverter.to_log_level("fatal") == LogLevel.Fatal

    def test_to_string(self):
        assert LogLevelConverter.to_string(LogLevel.Fatal) == "FATAL"

    def test_to_integer(self):
        assert LogLevelConverter.to_integer(LogLevel.Fatal) == 1
