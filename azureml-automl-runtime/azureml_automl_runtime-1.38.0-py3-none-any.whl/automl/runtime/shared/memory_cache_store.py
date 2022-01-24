# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Memory-based cache store."""
import copy
from typing import Iterable, Optional, Any, Dict

from .cache_store import CacheStore


class MemoryCacheStore(CacheStore):
    """MemoryCacheStore - stores value in memory."""

    def load(self):
        """Load from memory - NoOp."""
        pass

    def add(self, keys, values):
        """
        Add to store by creating a deep copy.

        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = copy.deepcopy(v)

    def get(self, keys: Iterable[str], default: Optional[Any] = None) -> Dict[Any, Optional[Any]]:
        """
        Retrieve & create a deepcopy before returning. The deepcopy is necessary to make sure
        the cache entry is unmodified.

        :param keys: Keys to retrieve.
        :param default: Default value if the key is not present.
        :return: Dictionary of keys, values.
        """
        ret = {}            # type: Dict[str, Optional[Any]]
        for key in keys:
            if key in self.cache_items:
                value = self.cache_items.get(key)
                if value is not None:
                    ret[key] = copy.deepcopy(value)
                else:
                    ret[key] = None
            else:
                ret[key] = default

        return ret

    def unload(self):
        """Unload from memory."""
        self.cache_items.clear()
