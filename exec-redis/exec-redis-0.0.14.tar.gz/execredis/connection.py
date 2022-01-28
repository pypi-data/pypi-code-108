from abc import ABC
from redis import ConnectionPool, StrictRedis
from rediscluster import ClusterConnectionPool, RedisCluster


class ExecRedisClient(RedisCluster, StrictRedis, ABC):
    def __new__(cls, host=None, db=0, cluster=False, redis_kwargs=None, **kwargs):
        __conn = RedisCluster if cluster else StrictRedis
        __conn_pool = ClusterConnectionPool if cluster else ConnectionPool
        return __conn(connection_pool=__conn_pool(host=host or 'localhost', db=db, **kwargs),
                      decode_responses=True, **(redis_kwargs or {}))
