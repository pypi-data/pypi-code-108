import codefast as cf
import requests
from codefast.patterns.singleton import SingletonMeta
from authc import authc
from rss.core.redis import RedisClient

REDIS_MAP = {
    'host': 'ali_redis_host',
    'port': 'ali_redis_port',
    'pass': 'ali_redis_pass'
}


class Spider(metaclass=SingletonMeta):
    # Simulate a normal web user
    def __init__(self) -> None:
        pass

    def born(self) -> requests.Session:
        spider = requests.Session()
        spider.encoding = 'utf-8'
        spider.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        })
        return spider


class AuthOnce(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._info = {}

    def info(self):
        if not self._info:
            self._info = authc()
        return self._info


class Initiator(object):
    @staticmethod
    def redis():
        try:
            auth = AuthOnce().info()
            m = REDIS_MAP
            host, port, passwd = m['host'], m['port'], m['pass']
            return RedisClient(auth[host], auth[port], auth[passwd])
        except KeyError:
            cf.error('Authentication failed {}'.format(auth))
            return None
        except Exception as e:
            cf.error('Redis connection failed', str(e))
            return None
