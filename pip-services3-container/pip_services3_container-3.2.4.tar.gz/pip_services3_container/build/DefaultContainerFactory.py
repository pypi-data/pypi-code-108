# -*- coding: utf-8 -*-
"""
    pip_services3_container.build.DefaultContainerFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Default container factory implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_components.auth import DefaultCredentialStoreFactory
from pip_services3_components.build import CompositeFactory, IFactory
from pip_services3_components.cache import DefaultCacheFactory
from pip_services3_components.config import DefaultConfigReaderFactory
from pip_services3_components.connect import DefaultDiscoveryFactory
from pip_services3_components.count import DefaultCountersFactory
from pip_services3_components.info.DefaultInfoFactory import DefaultInfoFactory
from pip_services3_components.log.DefaultLoggerFactory import DefaultLoggerFactory
from pip_services3_components.test.DefaultTestFactory import DefaultTestFactory
from pip_services3_components.trace.DefaultTracerFactory import DefaultTracerFactory


class DefaultContainerFactory(CompositeFactory):
    """
    Creates default container components (loggers, counters, caches, locks, etc.) by their descriptors.
    """

    def __init__(self, *factories: IFactory):
        """
        Create a new instance of the factory and sets nested factories.

        :param factories: a list of nested factories
        """
        super(DefaultContainerFactory, self).__init__(*factories)
        self.add(DefaultInfoFactory())
        self.add(DefaultLoggerFactory())
        self.add(DefaultCountersFactory())
        self.add(DefaultConfigReaderFactory())
        self.add(DefaultCacheFactory())
        self.add(DefaultCredentialStoreFactory())
        self.add(DefaultDiscoveryFactory())
        self.add(DefaultTestFactory())
        self.add(DefaultTracerFactory())
