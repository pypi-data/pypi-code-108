import os
import redis
from typing import Callable
from pytz import timezone
from c27cache.datetime_support import asia_kolkata
from c27cache.logger import log_debug


class C27Cache:
    redis_url: str
    namespace: str
    tz: timezone    

    @classmethod
    def init(
        cls,
        redis_url: str,
        tz: timezone = asia_kolkata,
        namespace: str = "c27cache",        
    ):
        cls.redis_url = redis_url
        cls.namespace = namespace
        cls.tz = tz        
        cls.redis_client = redis.Redis.from_url(redis_url)
        log_debug(msg=f"PING: {cls.redis_client.ping()}", loc=f"{__name__}")
        return cls

    @classmethod
    def __str__(cls):
        return f"<C27Cache redis_url={cls.redis_url}, namespace={cls.namespace} client={cls.redis_client}"
