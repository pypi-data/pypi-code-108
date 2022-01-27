# pylint: skip-file
import contextlib
import datetime
import hashlib
import json
import math
import time

from .exceptions import Backoff
from .exceptions import RateLimited
from .lock import Lock
from .manager import connections


__all__ = []


async def add(
    key: str,
    value: int = 1,
    using: str = 'default',
    *args, **kwargs
):
    """Create a counter under the given key, starting from ``0`` and
    incremented by `value`. Return the latest value.
    """
    return await connections[using].setcounter(key, value, *args, **kwargs)


@contextlib.asynccontextmanager
async def backoff(
    key: str,
    using: str = 'default',
    catch: type = Exception
) -> int:
    """Calculate an exponential backoff using a counter. Return an integer
    representing the remaining milliseconds.
    """
    now = int(time.time())
    expires = await get(f'{key}-expires', using=using)
    if expires is not None:
        expires = int.from_bytes(expires, 'big')
        if expires >= (now*1000):
            exception = Backoff(
                seconds=int(math.ceil(expires - (now*1000))/1000),
                expires=expires,
                attempts=int(await get(key, using=using)),
                timestamp=int.from_bytes(
                    await get(f'{key}-created', using=using),
                    'big'
                )
            )
            if exception.seconds > 0:
                raise exception

    try:
        yield
        await delete(key, using=using)
        await delete(f'{key}-created', using=using)
        await delete(f'{key}-expires', using=using)
    except catch as exception:
        # It is assumed here that any exception indicates that an operation
        # has failed and the backoff should be increased.
        now = int(time.time())
        count = await add(key, using=using)
        ttl = 0
        await set(
            key=f'{key}-created',
            value=int.to_bytes(now * 1000, 8, 'big'),
            using=using
        )
        if count > 1:
            ttl = math.ceil(0.5 * ((2**(count)) - 1))
            await set(
                key=f'{key}-expires',
                value=int.to_bytes((now + ttl)*1000, 8, 'big'),
                using=using,
                expires=ttl*1000
            )
            Backoff.add_to_exception(
                exception,
                ttl,
                expires=(now + ttl)*1000,
                attempts=count,
                timestamp=now*1000
            )
        raise


@contextlib.asynccontextmanager
async def ratelimit(
    key: str,
    ttl: int,
    using: str = 'default'
):
    """Enforce a rudimentary rate-limiting mechanism for the given key."""
    key = f'{key}-ratelimit'
    now = int(time.time() * 1000)
    dto = await get(key, using=using)
    if dto is not None:
        # The cache backend is assumed to remove the key if the ratelimit
        # expires.
        raise Backoff.fromserialized(dto)

    await set(
        key=key,
        value=json.dumps({
            'expires': now + (ttl*1000),
            'timestamp': now
        }),
        expires=ttl*1000,
        using=using
    )
    yield



async def clear(using: str):
    """Purges all keys from the cache."""
    return await connections[using].clear()


async def delete(key, using='default', *args, **kwargs):
    """Delete the given `key` from the cache, if it exists."""
    kwargs.setdefault('version', 1)
    return await connections[using].delete(key, *args, **kwargs)


async def filter(pattern: str, using: str = 'default'):
    """Filter keys in the cache by the given match pattern."""
    return connections[using].filter(pattern)


async def get(key, using='default', *args, **kwargs):
    """Return given `key` from the cache `using`."""
    kwargs.setdefault('version', 1)
    return await connections[using].get(key, *args, **kwargs)


async def purge(using: str) -> None:
    """Purges all keys from the cache, for all versions."""
    return await connections[using].purge()


async def set(key, value, using='default', *args, **kwargs):
    """Set the given `key` to `value`."""
    kwargs.setdefault('version', 1)
    return await connections[using].set(key, value, *args, **kwargs)
