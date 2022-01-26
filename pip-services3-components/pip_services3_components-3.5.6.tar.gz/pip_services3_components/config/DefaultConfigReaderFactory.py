# -*- coding: utf-8 -*-
"""
    pip_services3_components.connect.DefaultConfigReaderFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Default discovery factory implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer.Descriptor import Descriptor

from .JsonConfigReader import JsonConfigReader
from .MemoryConfigReader import MemoryConfigReader
from .YamlConfigReader import YamlConfigReader
from ..build.Factory import Factory


class DefaultConfigReaderFactory(Factory):
    """
    Creates :class:`IConfigReader <pip_services3_components.config.IConfigReader.IConfigReader>` components by their descriptors.

    See :class:`Factory <pip_services3_components.build.Factory.Factory>`,
    :class:`MemoryConfigReader <pip_services3_components.config.MemoryConfigReader.MemoryConfigReader>`,
    :class:`JsonConfigReader <pip_services3_components.config.JsonConfigReader.JsonConfigReader>`,
    :class:`YamlConfigReader <pip_services3_components.config.YamlConfigReader.YamlConfigReader>`
    """

    MemoryConfigReaderDescriptor = Descriptor("pip-services", "config-reader", "memory", "*", "1.0")
    JsonConfigReaderDescriptor = Descriptor("pip-services", "config-reader", "json", "*", "1.0")
    YamlConfigReaderDescriptor = Descriptor("pip-services", "config-reader", "yaml", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()
        self.register_as_type(DefaultConfigReaderFactory.MemoryConfigReaderDescriptor, MemoryConfigReader)
        self.register_as_type(DefaultConfigReaderFactory.JsonConfigReaderDescriptor, JsonConfigReader)
        self.register_as_type(DefaultConfigReaderFactory.YamlConfigReaderDescriptor, YamlConfigReader)
