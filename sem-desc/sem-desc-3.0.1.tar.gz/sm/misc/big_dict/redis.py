import pickle
from typing import TypeVar, Dict, Union, Any

import redis

from sm.misc.big_dict.inmem import K, V, CacheDictStore


class RedisStore(Dict[K, V]):
    instance = None

    def __init__(self, url):
        self.url = url
        self.redis = redis.Redis.from_url(url)

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def __contains__(self, item: str):
        return self.redis.exists(item) == 1

    def __getitem__(self, item: str):
        assert item is not None, item
        resp = self.redis.get(item)
        if resp is None:
            raise KeyError(item)
        return self.deserialize(resp)

    def __setitem__(self, key: str, value: Union[str, bytes]):
        self.redis.set(key, value)

    def __len__(self):
        return self.redis.dbsize()

    def cache_dict(self) -> 'CacheDictStore[K, V]':
        """Return a version of the store that will cache all of the query for faster processing"""
        return CacheDictStore(self)

    def deserialize(self, value: str):
        return value


class PickleRedisStore(RedisStore[K, V]):

    def __setitem__(self, key: str, value: Any):
        value = pickle.dumps(value)
        self.redis.set(key, value)

    def deserialize(self, value: bytes):
        return pickle.loads(value)