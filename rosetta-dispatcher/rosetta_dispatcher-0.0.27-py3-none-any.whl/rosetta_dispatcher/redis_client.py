import redis

from rosetta_dispatcher.singleton import Singleton


class RedisClient(metaclass=Singleton):
    def __init__(self, host, port, password=None, decode_responses=True):
        self.pool = redis.ConnectionPool(host=host, port=port, password=password, decode_responses=decode_responses,
                                         socket_connect_timeout=5, socket_timeout=90, health_check_interval=90)

    @property
    def conn(self):
        return redis.Redis(connection_pool=self.pool)