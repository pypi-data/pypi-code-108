# -*- coding: utf-8 -*-
"""
    pip_services3_components.cache.DefaultCacheFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Default cache factory implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer.Descriptor import Descriptor

from .MemoryCache import MemoryCache
from .NullCache import NullCache
from ..build.Factory import Factory


class DefaultCacheFactory(Factory):
    """
    Creates :class:`ICache <pip_services3_components.cache.ICache.ICache>` components by their descriptors.

    See :class:`Factory <pip_services3_components.build.Factory.Factory>`,
    :class:`ICache <pip_services3_components.cache.ICache.ICache>`,
    :class:`MemoryCache <pip_services3_components.cache.MemoryCache.MemoryCache>`,
    :class:`NullCache <pip_services3_components.cache.NullCache.NullCache>`
    """
    
    NullCacheDescriptor = Descriptor("pip-services", "cache", "null", "*", "1.0")
    MemoryCacheDescriptor = Descriptor("pip-services", "cache", "memory", "*", "1.0")
    descriptor = Descriptor("pip-services", "factory", "cache", "default", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super().__init__()
        self.register_as_type(DefaultCacheFactory.NullCacheDescriptor, NullCache)
        self.register_as_type(DefaultCacheFactory.MemoryCacheDescriptor, MemoryCache)
