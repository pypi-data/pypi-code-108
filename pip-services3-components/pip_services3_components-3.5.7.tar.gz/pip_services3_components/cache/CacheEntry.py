# -*- coding: utf-8 -*-
"""
    pip_services3_components.cache.CacheEntry
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Cache entry implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time
from typing import Any


class CacheEntry(object):
    """
    Data object to store cached values with their keys used by :class:`MemoryCache <pip_services3_components.cache.MemoryCache.MemoryCache>`
    """

    def __init__(self, key: str, value: str, timeout: int):
        """
        Creates a new instance of the cache entry and assigns its values.

        :param key: a unique key to locate the value.

        :param value: a value to be stored.

        :param timeout: expiration timeout in milliseconds.
        """
        self.__key = key
        self.__value = value
        self.__expiration = time.perf_counter() * 1000 + timeout

    def get_key(self) -> str:
        """
        Gets the key to locate the cached value.

        :return: the value key.
        """
        return self.__key

    def get_value(self) -> Any:
        """
        Gets the cached value.

        :return: the value object.
        """
        return self.__value

    def get_expiration(self) -> int:
        """
        Gets the expiration timeout.

        :return: the expiration timeout in milliseconds.
        """
        return int(self.__expiration)

    def set_value(self, value: Any, timeout: int):
        """
        Sets a new value and extends its expiration.

        :param value: a new cached value.

        :param timeout: a expiration timeout in milliseconds.
        """
        self.__value = value
        self.__expiration = time.perf_counter() * 1000 + timeout

    def is_expired(self) -> bool:
        """
        Checks if this value already expired.

        :return: true if the value already expires and false otherwise.
        """
        return self.__expiration < time.perf_counter() * 1000
