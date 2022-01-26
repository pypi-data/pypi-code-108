# -*- coding: utf-8 -*-
"""
    pip_services3_components.config.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains implementation of the config design pattern.

    ConfigReader's Parameterize method allows us to take a standard configuration, and,
    using a set of current parameters (e.g. environment variables), parameterize it. When
    we create the configuration of a container, we can use environment variables to tailor
    it to the system, dynamically add addresses, ports, etc.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'IConfigReader', 'ConfigReader', 'MemoryConfigReader',
    'FileConfigReader', 'JsonConfigReader', 'YamlConfigReader',
    'DefaultConfigReaderFactory'
]

from .ConfigReader import ConfigReader
from .DefaultConfigReaderFactory import DefaultConfigReaderFactory
from .FileConfigReader import FileConfigReader
from .IConfigReader import IConfigReader
from .JsonConfigReader import JsonConfigReader
from .MemoryConfigReader import MemoryConfigReader
from .YamlConfigReader import YamlConfigReader
