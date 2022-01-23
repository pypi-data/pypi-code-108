from typing import Any, Optional
from urllib.parse import urlparse

from redis import Redis
from redis.sentinel import Sentinel

from freiner.errors import FreinerConfigurationError

from .redis import RedisStorage


class RedisSentinelStorage(RedisStorage):
    """
    Rate limit storage with redis sentinel as backend.

    Depends on `redis` library.
    """

    def __init__(self, sentinel: Sentinel, service_name: str) -> None:
        self._sentinel: Sentinel = sentinel
        self._service_name: str = service_name

        self._sentinel_master: Redis = self._sentinel.master_for(self._service_name)
        self._sentinel_slave: Redis = self._sentinel.slave_for(self._service_name)

        super().__init__(self._sentinel_master)

    @classmethod
    def from_uri(
        cls, uri: str, service_name: Optional[str] = None, **options: Any
    ) -> "RedisSentinelStorage":
        """
        :param uri: URI of the form `redis+sentinel://host:port,host:port/service_name`
        :param service_name: Sentinel service name (if not provided in `uri`).
        :param options: All remaining keyword arguments are passed directly to the constructor
                        of :class:`redis.sentinel.Sentinel`.
        :raises FreinerConfigurationError: When no service name is provided.
        """

        parsed_uri = urlparse(uri)
        sentinel_configuration = []

        password = None
        if parsed_uri.password:
            password = parsed_uri.password

        for loc in parsed_uri.netloc[parsed_uri.netloc.find("@") + 1 :].split(","):
            host, port = loc.split(":")
            sentinel_configuration.append((host, int(port)))

        service_name = parsed_uri.path.replace("/", "") if parsed_uri.path else service_name
        if service_name is None:
            raise FreinerConfigurationError("'service_name' not provided")

        options.setdefault("socket_timeout", 0.2)

        sentinel = Sentinel(sentinel_configuration, password=password, **options)
        return cls(sentinel, service_name)

    def get(self, key: str) -> int:
        """
        Retrieve the current request count for the given rate limit key.

        :param key: The key to get the counter value for.
        """

        return self._get(key, self._sentinel_slave)

    def get_expiry(self, key: str) -> float:
        """
        Retrieve the expected expiry time for the given rate limit key.

        :param key: The key to get the expiry time for.
        :return: The time at which the current rate limit for the given key ends.
        """

        return self._get_expiry(key, self._sentinel_slave)

    def check(self) -> bool:
        """
        Check if the connection to the storage backend is healthy.
        """

        return self._check(self._sentinel_slave)


__all__ = [
    "RedisSentinelStorage",
]
