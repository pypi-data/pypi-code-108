# -*- coding: utf-8 -*-
"""
    tests.build.test_Factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer import Descriptor

from pip_services3_components.log import DefaultLoggerFactory
from pip_services3_components.log import LogLevel


class TestFactory:

    def test_can_create(self):
        factory = DefaultLoggerFactory()
        assert None is factory.can_create(111)

        descriptor = Descriptor('*', 'logger', 'console', '*', '*')
        assert descriptor == factory.can_create(descriptor)

    def test_create(self):
        factory = DefaultLoggerFactory()
        descriptor = Descriptor('*', 'logger', 'console', '*', '*')
        logger = factory.create(descriptor)

        assert not (logger is None)

        logger.set_level(LogLevel.Error)
        logger.trace(None, 'Hello world!')
