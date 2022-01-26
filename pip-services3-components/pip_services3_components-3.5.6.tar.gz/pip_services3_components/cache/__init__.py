# -*- coding: utf-8 -*-
"""
    pip_services3_components.cache.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Abstract implementation of various distributed caches. We can save an object
    to cache and retrieve it object by its key, using various implementations.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'ICache', 'CacheEntry', 'NullCache',
    'MemoryCache', 'DefaultCacheFactory'
]

from .CacheEntry import CacheEntry
from .DefaultCacheFactory import DefaultCacheFactory
from .ICache import ICache
from .MemoryCache import MemoryCache
from .NullCache import NullCache
