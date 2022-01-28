# -*- coding: utf-8 -*-
"""
    pip_services3_components.cache.ICache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for caching components.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import Any, Optional


class ICache(ABC):
    """
    Interface for caches that are used to cache values to improve performance.
    """

    def retrieve(self, correlation_id: Optional[str], key: str) -> Any:
        """
        Retrieves cached value from the cache using its key.
        If value is missing in the cache or expired it returns None.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.

        :return: a cached value or None if value wasn't found or timeout expired.
        """
        raise NotImplementedError('Method from interface definition')

    def store(self, correlation_id: Optional[str], key: str, value: Any, timeout: int) -> Any:
        """
        Stores value in the cache with expiration time.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.

        :param value: a value to store.

        :param timeout: expiration timeout in milliseconds.

        :return: a cached value stored in the cache.
        """
        raise NotImplementedError('Method from interface definition')

    def remove(self, correlation_id: Optional[str], key: str):
        """
        Removes a value from the cache by its key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param key: a unique value key.
        """
        raise NotImplementedError('Method from interface definition')
