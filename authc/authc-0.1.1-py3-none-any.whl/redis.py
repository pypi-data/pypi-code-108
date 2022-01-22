from pydantic import RedisDsn
from redis import StrictRedis
from redis.exceptions import ConnectionError
from authc.core import authc


def get_redis_cn():
    a = authc()
    host, port, password = a['ali_redis_host'], a['ali_redis_port'], a[
        'ali_redis_pass']
    return StrictRedis(host=host, port=port, password=password)


def get_redis():
    x = authc()
    host, port, password = x['redis_host'], x['redis_port'], x['redis_pass']
    return StrictRedis(host=host, port=port, password=password)
    
