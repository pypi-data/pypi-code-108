# -*- coding: utf-8 -*-
"""
    pip_services3_components.log.DefaultLoggerFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Default logger factory implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer.Descriptor import Descriptor

from .CompositeLogger import CompositeLogger
from .ConsoleLogger import ConsoleLogger
from .NullLogger import NullLogger
from ..build.Factory import Factory


class DefaultLoggerFactory(Factory):
    """
    Creates :class:`ILogger <pip_services3_components.log.ILogger.ILogger>` components by their descriptors.

    See :class:`Factory <pip_services3_components.build.Factory.Factory>`,
    :class:`NullLogger <pip_services3_components.log.NullLogger.NullLogger>`,
    :class:`ConsoleLogger <pip_services3_components.log.ConsoleLogger.ConsoleLogger>`,
    :class:`CompositeLogger <pip_services3_components.log.CompositeLogger.CompositeLogger>`
    """

    NullLoggerDescriptor = Descriptor("pip-services", "logger", "null", "*", "1.0")
    ConsoleLoggerDescriptor = Descriptor("pip-services", "logger", "console", "*", "1.0")
    CompositeLoggerDescriptor = Descriptor("pip-services", "logger", "composite", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()
        self.register_as_type(DefaultLoggerFactory.NullLoggerDescriptor, NullLogger)
        self.register_as_type(DefaultLoggerFactory.ConsoleLoggerDescriptor, ConsoleLogger)
        self.register_as_type(DefaultLoggerFactory.CompositeLoggerDescriptor, CompositeLogger)
