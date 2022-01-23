import time
from typing import Any, Callable, Tuple, cast

import redis

from . import MovingWindow


class RedisInteractor:
    SCRIPT_MOVING_WINDOW = """
        local items = redis.call('lrange', KEYS[1], 0, tonumber(ARGV[2]))
        local expiry = tonumber(ARGV[1])
        local a = 0
        local oldest = nil
        for idx=1,#items do
            if tonumber(items[idx]) > expiry then
                a = a + 1
                if oldest == nil then
                    oldest = tonumber(items[idx])
                end
            else
                break
            end
        end
        return {oldest, a}
        """

    SCRIPT_ACQUIRE_MOVING_WINDOW = """
        local entry = redis.call('lindex', KEYS[1], tonumber(ARGV[2]) - 1)
        local timestamp = tonumber(ARGV[1])
        local expiry = tonumber(ARGV[3])
        if entry and tonumber(entry) > timestamp - expiry then
            return false
        end
        local limit = tonumber(ARGV[2])
        local no_add = tonumber(ARGV[4])
        if no_add == 0 then
            redis.call('lpush', KEYS[1], timestamp)
            redis.call('ltrim', KEYS[1], 0, limit - 1)
            redis.call('expire', KEYS[1], expiry)
        end
        return true
        """

    SCRIPT_CLEAR_KEYS = """
        local keys = redis.call('keys', KEYS[1])
        local res = 0
        for i=1,#keys,5000 do
            res = res + redis.call(
                'del', unpack(keys, i, math.min(i+4999, #keys))
            )
        end
        return res
        """

    SCRIPT_INCR_EXPIRE = """
        local current
        current = redis.call("incr", KEYS[1])
        if tonumber(current) == 1 then
            redis.call("expire", KEYS[1], ARGV[1])
        end
        return current
    """

    def initialize_storage(self, connection: redis.Redis):
        moving_window_script = connection.register_script(self.SCRIPT_MOVING_WINDOW)
        self.lua_moving_window = cast(
            Callable[[Tuple[str], Tuple[float, int]], Tuple[float, int]],
            moving_window_script,
        )

        acquire_window_script = connection.register_script(self.SCRIPT_ACQUIRE_MOVING_WINDOW)
        self.lua_acquire_window = cast(
            Callable[[Tuple[str], Tuple[float, int, int, int]], bool],
            acquire_window_script,
        )

        clear_keys_script = connection.register_script(self.SCRIPT_CLEAR_KEYS)
        self.lua_clear_keys = cast(
            Callable[[Tuple[str]], int],
            clear_keys_script,
        )

        incr_expire_script = connection.register_script(RedisStorage.SCRIPT_INCR_EXPIRE)
        self.lua_incr_expire = cast(
            Callable[[Tuple[str], Tuple[int]], int],
            incr_expire_script,
        )

    def get_moving_window(self, key: str, limit: int, expiry: int) -> MovingWindow:
        """
        Retrieves the starting point and the number of entries in the moving window.

        :param key: The rate limit key to retrieve statistics about.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :return: (start of window, number of acquired entries)
        """

        timestamp = time.time()
        window = self.lua_moving_window((key,), (timestamp - expiry, limit))
        return MovingWindow(window[0], window[1])

    def _incr(self, key: str, expiry: int, connection: redis.Redis, elastic_expiry: bool = False):
        """
        Increments the counter for the given rate limit key.

        :param key: The key to increment.
        :param expiry: Amount in seconds for the key to expire in.
        :param connection: Redis connection.
        :param elastic_expiry: Whether to keep extending the rate limit window every hit.
        :return: The number of hits currently on the rate limit for the given key.
        """

        value = connection.incr(key)
        if elastic_expiry or value == 1:
            connection.expire(key, expiry)
        return value

    def _get(self, key: str, connection: redis.Redis) -> int:
        """
        Retrieve the current request count for the given rate limit key.

        :param key: The key to get the counter value for.
        :param connection: Redis connection.
        """

        return int(connection.get(key) or 0)

    def _clear(self, key: str, connection: redis.Redis) -> None:
        """
        Resets the rate limit for the given key.

        :param key: The key to clear rate limits for.
        :param connection: Redis connection.
        """

        connection.delete(key)

    def _reset(self) -> int:
        return self.lua_clear_keys(("LIMITER*",))

    def _acquire_entry(
        self, key: str, limit: int, expiry: int, connection: redis.Redis, no_add: bool = False
    ) -> bool:
        """
        :param key: The rate limit key to acquire an entry in.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :param connection: Redis connection.
        :param no_add: If False, an entry is not actually acquired but instead serves as a 'check'.
        """

        timestamp = time.time()
        acquired = self.lua_acquire_window(
            (key,),
            (timestamp, limit, expiry, int(no_add)),
        )
        return bool(acquired)

    def _get_expiry(self, key: str, connection: redis.Redis) -> float:
        """
        Retrieve the expected expiry time for the given rate limit key.

        :param key: The key to get the expiry time for.
        :param connection: Redis connection.
        :return: The time at which the current rate limit for the given key ends.
        """

        return max(connection.ttl(key), 0) + time.time()

    def _check(self, connection: redis.Redis) -> bool:
        """
        Check if the connection to the storage backend is healthy.

        :param connection: Redis connection.
        """

        try:
            return connection.ping()
        except:  # noqa
            return False


class RedisStorage(RedisInteractor):
    """
    Rate limit storage with redis as backend.

    Depends on the `redis` library.
    """

    def __init__(self, client: redis.Redis) -> None:
        self._client = client
        self.initialize_storage(self._client)

    @classmethod
    def from_uri(cls, uri: str, **options: Any) -> "RedisStorage":
        """
        :param uri: URI of the form `redis://[:password]@host:port`, `redis://[:password]@host:port/db`,
                    `rediss://[:password]@host:port`, `unix:///path/to/sock` etc. This uri is passed
                    directly to :func:`redis.from_url`.
        :param options: All remaining keyword arguments are passed directly to the constructor
                        of :class:`redis.Redis`.
        """

        client: redis.Redis = redis.from_url(uri, **options)
        return cls(client)

    def incr(self, key: str, expiry: int, elastic_expiry: bool = False) -> int:
        """
        Increments the counter for the given rate limit key.

        :param key: The key to increment.
        :param expiry: Amount in seconds for the key to expire in.
        :param elastic_expiry: Whether to keep extending the rate limit window every hit.
        :return: The number of hits currently on the rate limit for the given key.
        """

        if elastic_expiry:
            return self._incr(key, expiry, self._client, elastic_expiry)
        else:
            return self.lua_incr_expire((key,), (expiry,))

    def get(self, key: str) -> int:
        """
        Retrieve the current request count for the given rate limit key.

        :param key: The key to get the counter value for.
        """

        return self._get(key, self._client)

    def clear(self, key: str) -> None:
        """
        Resets the rate limit for the given key.

        :param key: The key to clear rate limits for.
        """

        self._clear(key, self._client)

    def acquire_entry(self, key: str, limit: int, expiry: int, no_add: bool = False) -> bool:
        """
        :param key: The rate limit key to acquire an entry in.
        :param limit: The total amount of entries allowed before hitting the rate limit.
        :param expiry: Amount in seconds for the acquired entry to expire in.
        :param no_add: If False, an entry is not actually acquired but instead serves as a 'check'.
        """

        return self._acquire_entry(key, limit, expiry, self._client, no_add=no_add)

    def get_expiry(self, key: str) -> float:
        """
        Retrieve the expected expiry time for the given rate limit key.

        :param key: The key to get the expiry time for.
        :return: The time at which the current rate limit for the given key ends.
        """

        return self._get_expiry(key, self._client)

    def check(self) -> bool:
        """
        Check if the connection to the storage backend is healthy.
        """

        return self._check(self._client)

    def reset(self) -> None:
        """
        This function calls a Lua Script to delete keys prefixed with 'LIMITER'
        in blocks of 5000.

        .. warning::
           This operation was designed to be fast, but was not tested
           on a large production based system. Be careful with its usage as it
           could be slow on very large data sets.
        """

        self._reset()


__all__ = [
    "RedisInteractor",
    "RedisStorage",
]
