import aioredis
from redis import StrictRedis

from .config import redis_config

redis = StrictRedis.from_url(redis_config.get('url'), decode_responses=True)


def get_async_redis(loop):
    return loop.run_until_complete(
        aioredis.create_redis_pool(
            redis_config.get('url'),
            loop=loop,
            encoding='utf-8'
        )
    )
