from json import loads, dumps
from time import time
from typing import List, cast

from redis import Redis as RedisClient

from flypper.entities.flag import Flag, FlagData, UnversionedFlagData
from flypper.storage.abstract import AbstractStorage

class RedisStorage(AbstractStorage):
    def __init__(self, redis: RedisClient, prefix: str = "flypper"):
        self._version_key = f"{prefix}:version"
        self._history_key = f"{prefix}:history"
        self._flag_prefix = f"{prefix}:flags"
        self._redis = redis

    def list(self, version__gt: int = 0) -> List[Flag]:
        flag_names = self._redis.zrange(self._history_key, version__gt, -1)

        # Don't try to call Redis if there is no flag name
        if not flag_names:
            return []

        return [
            Flag(data=cast(FlagData, loads(flag_json)))
            for flag_json in self._redis.mget(
                [self._flag_key(flag_name.decode("UTF-8")) for flag_name in flag_names]
            )
            if flag_json
        ]

    def upsert(self, flag_data: UnversionedFlagData) -> Flag:
        version = self._redis.incr(self._version_key)
        flag_name = flag_data["name"]
        data: FlagData = {
            "name": flag_data["name"],
            "deleted": flag_data["deleted"],
            "enabled": flag_data["enabled"],
            "enabled_for_actors": flag_data["enabled_for_actors"],
            "enabled_for_percentage_of_actors": flag_data["enabled_for_percentage_of_actors"],
            "updated_at": time(),
            "version": version,
        }
        self._redis.set(self._flag_key(flag_name), dumps(data))
        self._redis.zadd(self._history_key, {flag_name: version})
        return Flag(data=cast(FlagData, data))

    def delete(self, flag_name: str) -> None:
        self._redis.delete(self._flag_key(flag_name))
        self._redis.zrem(self._history_key, flag_name)

    def _flag_key(self, flag_name):
        return f"{self._flag_prefix}:{flag_name}"
