# -*- coding: utf-8 -*-
"""
    tests.log.test_ConsoleLogger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_components.log import ConsoleLogger
from .LoggerFixture import LoggerFixture


class TestConsoleLogger:
    log = None
    fixture = None

    def setup_method(self, method):
        self.log = ConsoleLogger()
        self.fixture = LoggerFixture(self.log)

    def test_log_level(self):
        self.fixture.test_log_level()

    def test_text_output(self):
        self.fixture.test_text_output()
