import redis
import os
from django.conf import settings


class RedisWrapper:
    _CONNECTION = None

    @classmethod
    def client(cls):
        if cls._CONNECTION is None:
            cls._CONNECTION = redis.Redis(
                host=os.environ.get('REDIS_HOST'),
                port=int(os.environ.get('REDIS_PORT')),
                password=os.environ.get('REDIS_PASSWORD')
            )
        return cls._CONNECTION

    @classmethod
    def ping(cls):
        return cls.client().ping()

    @classmethod
    def get(cls, key):
        if cls.key_exists(key):
            value = cls.client().get(key)
            return value.decode("utf-8") if value else None

        return None

    @classmethod
    def get_dict(cls, hash_key):
        if cls.key_exists(hash_key):
            return {key.decode("utf-8"): value.decode("utf-8") for key, value in cls.client().hgetall(hash_key).items()}

        return None

    @classmethod
    def set(cls, key, value):
        return cls.client().set(key, value)

    @classmethod
    def set_dict(cls, name, key, value):
        return cls.client().hset(name, key, value)

    @classmethod
    def key_exists(cls, key):
        return cls.client().exists(key)

    @classmethod
    def dict_key_exists(cls, name, key):
        return cls.client().hexists(name, key)

    @classmethod
    def delete(cls, keys):
        if isinstance(keys, list):
            for key in keys:
                cls.client().delete(key)
            return True
        else:
            return cls.client().delete(keys)

    @classmethod
    def delete_dict_key(cls, name, key):
        return cls.client().hdel(name, key)

    @classmethod
    def set_ttl(cls, key, ttl=settings.HTG_URL_SETTINGS.get('HTG_URL_REDIS_TTL')):
        if cls.key_exists(key):
            return cls.client().expire(key, ttl)

        return None

    @classmethod
    def check_ttl(cls, key):
        if cls.key_exists(key):
            return cls.client().ttl(key)

        return None

    @classmethod
    def get_keys(cls, pattern='*'):
        return [key.decode('utf-8') for key in cls.client().keys(pattern)]
