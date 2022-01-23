from typing import Any
from urllib.parse import urlparse

from rediscluster import RedisCluster

from .redis import RedisStorage


class RedisClusterStorage(RedisStorage):
    """
    Rate limit storage with redis cluster as backend.

    Depends on `redis-py-cluster` library.
    """

    @classmethod
    def from_uri(cls, uri: str, **options: Any) -> "RedisClusterStorage":
        """
        :param uri: URI of the form `redis+cluster://[:password]@host:port,host:port`
        :param options: All remaining keyword arguments are passed directly to the constructor
                        of :class:`rediscluster.RedisCluster`.
        """

        parsed_uri = urlparse(uri)
        cluster_hosts = []
        for loc in parsed_uri.netloc.split(","):
            host, port = loc.split(":")
            cluster_hosts.append({"host": host, "port": int(port)})

        options.setdefault("max_connections", 1000)
        options["startup_nodes"] = cluster_hosts

        client = RedisCluster(**options)
        return cls(client)

    def reset(self) -> None:
        """
        Redis Clusters are sharded and deleting across shards
        can't be done atomically. Because of this, this reset loops over all
        keys that are prefixed with 'LIMITER' and calls delete on them, one at
        a time.

        .. warning::
         This operation was not tested with extremely large data sets.
         On a large production based system, care should be taken with its
         usage as it could be slow on very large data sets.
        """

        keys = self._client.keys("LIMITER*")
        for key in keys:
            self._client.delete(key.decode("utf-8"))


__all__ = [
    "RedisClusterStorage",
]
