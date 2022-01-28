#!/usr/bin/env python
import redis
from cryptography.fernet import Fernet


class Authorization(Fernet):
    def __init__(self, redis_host: str, redis_port: int, redis_password: str,
                 fernet_key: bytes):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.fernet = Fernet(fernet_key)

    @property
    def redis(self):
        self.__redis = redis.StrictRedis(host=self.redis_host,
                                       port=self.redis_port,
                                       password=self.redis_password)
        return self.__redis

    def get(self, key: str) -> str:
        '''Get value from redis and decrypt with fernet.'''
        _value = self.redis.get(key)
        return self.fernet.decrypt(_value).decode()

    def set(self, key: str, value: str) -> None:
        __ = self.fernet.encrypt(str(value).encode())
        self.redis.set(key, __)
