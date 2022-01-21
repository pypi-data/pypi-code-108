import os
import contextlib
import json
from abc import ABC, abstractmethod


@contextlib.contextmanager
def tempenv(**update):
    """
    Temporarily updates the ``os.environ``
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    previous_values = {k: env.get(k, None) for k in update}
    for k, v in update.items():
        env[k] = v
    yield
    for k, v in previous_values.items():
        if v is None:
            # means that it was not an existing key before the updating operation
            env.pop(k)
        else:
            env[k] = v


class CachingEngine(ABC):
    @abstractmethod
    def set(self, key: str, val: str):
        pass

    @abstractmethod
    def get_cache_or_none(self, key: str):
        pass


class Cached:
    """cache a function that returns jsonifiable output"""

    def __init__(self, cache_key_func, caching_engine: CachingEngine, should_cache=None):
        self.cache_key_func = cache_key_func
        self.caching_engine = caching_engine
        self._should_cache = should_cache

    def should_cache(self, *args, **kwargs):
        if self._should_cache is None:
            return True
        else:
            return self._should_cache(*args, **kwargs)

    def __call__(self, function_to_be_decorated):
        def new_func(*args, **kwargs):
            key = self.cache_key_func(*args, **kwargs)
            cached_value = self.caching_engine.get_cache_or_none(key)
            if cached_value is None:
                val = function_to_be_decorated(*args, **kwargs)
                if self.should_cache(*args, value_to_cache=val, **kwargs):
                    self.caching_engine.set(key, json.dumps(val))
                return val
            else:
                return cached_value

        return new_func


class AsyncCached:
    """cache a function that returns jsonifiable output"""

    def __init__(self, cache_key_func, caching_engine: CachingEngine, should_cache=None):
        self.cache_key_func = cache_key_func
        self.caching_engine = caching_engine
        self._should_cache = should_cache

    def should_cache(self, *args, **kwargs):
        if self._should_cache is None:
            return True
        else:
            return self._should_cache(*args, **kwargs)

    def __call__(self, function_to_be_decorated):
        async def new_func(*args, **kwargs):
            key = self.cache_key_func(*args, **kwargs)
            cached_value = self.caching_engine.get_cache_or_none(key)
            if cached_value is None:
                val = await function_to_be_decorated(*args, **kwargs)
                if self.should_cache(*args, value_to_cache=val, **kwargs):
                    self.caching_engine.set(key, json.dumps(val))
                return val
            else:
                return cached_value

        return new_func


class RedisCachingEngine(CachingEngine):
    def __init__(self, redis_client, exp):
        self.redis_client = redis_client
        self.exp = exp

    def get_cache_or_none(self, key):
        cache_value = self.redis_client.get(key)
        if cache_value is None:
            return None
        else:
            return json.loads(cache_value)

    def set(self, k, v):
        self.redis_client.set(k, v, ex=self.exp)


class RedisCached(Cached):
    def __init__(self, redis_client, key_func, exp, should_cache=None):
        return super().__init__(key_func, RedisCachingEngine(redis_client, exp), should_cache)


class AsyncRedisCached(AsyncCached):
    def __init__(self, redis_client, key_func, exp, should_cache=None):
        return super().__init__(key_func, RedisCachingEngine(redis_client, exp), should_cache)
