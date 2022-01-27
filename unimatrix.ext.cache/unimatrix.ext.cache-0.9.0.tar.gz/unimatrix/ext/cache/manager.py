"""Declares :class:`CacheManager`."""
import asyncio

import ioc.loader
from unimatrix.lib.datastructures import ImmutableDTO


class CacheManager:
    """Manages connection pools."""
    __backends = {
        'redis': 'unimatrix.ext.cache.redis.RedisCache'
    }

    def __init__(self):
        self.__connections = {}

    def add(self, name, opts):
        """Add a named cache connection `name` with the given
        options `opts`.
        """
        cls = ioc.loader.import_symbol(
            self.__backends[ opts['backend'] ])
        self.__connections[name] = cls(ImmutableDTO.fromdict(opts))

    async def connect(self):
        """Connect all caches that are known by the manager."""
        futures = []
        for cache in dict.values(self.__connections):
            futures.append(cache.connect())
        await asyncio.gather(*futures)

    async def destroy(self):
        """Destroys all connections and empties the registry."""
        for connection in dict.values(self.__connections):
            connection.close()
            await connection.join()

    def __getitem__(self, using):
        if using not in self.__connections:
            raise KeyError(
                f"Connection does not exist: {using}. "
                f"Choose from: {', '.join(self.__connections.keys())}"
            )
        return self.__connections[using]


connections = CacheManager()
del CacheManager
