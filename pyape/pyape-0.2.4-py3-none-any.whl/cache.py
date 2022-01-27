"""
pyape.cache
~~~~~~~~~~~~~~~~~~~
提供全局缓存的读取和写入
"""
import warnings
import pickle
from pyape import uwsgiproxy
from pyape.flask_redis import FlaskRedis


class Cache(object):
    """ 处理缓存
    在 UWSGI 中运行的时候，使用 UWSGI 的缓存机制，实现进程间共享
    否则，在内存中保存缓存
    """
    def __init__(self, ctype):
        self.ctype = ctype


class UwsgiCache(Cache):
    def __init__(self):
        super().__init__('uwsgi')

    def __getitem__(self, name):
        """
        获取 UWSGI 缓存
        :param name: 真实的 name，带有 regional 信息
        :return: 序列化之后的 python 对象
        """
        raw_value = uwsgiproxy.cache_get(name)
        # print('_getuwsgicache:', raw_value)
        if raw_value is not None:
            return pickle.loads(raw_value, encoding='utf8')
        return None

    def __setitem__(self, name, value):
        """
        设置 UWSGI 缓存
        :param name: 设置名称
        :param value:
        :return:
        """
        if value is None:
            uwsgiproxy.cache_del(name)
            return
        raw_value = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        # print('_setuwsgicache:', raw_value)
        if uwsgiproxy.cache_exists(name):
            uwsgiproxy.cache_update(name, raw_value)
        else:
            uwsgiproxy.cache_set(name, raw_value)


class DictCache(Cache):
    """ 使用一个 Python Dict 保存缓存
    仅用于测试，应该在 单线程/单进程 本地环境使用
    """
    def __init__(self):
        super().__init__('dict')
        self.__g = {}

    def __getitem__(self, name):
        return self.__g.get(name)

    def __setitem__(self, name, value):
        self.__g[name] = value


class RedisCache(Cache):
    def __init__(self, flask_redis_client):
        super().__init__('redis')
        self.__client = flask_redis_client
        if isinstance(self.__client, FlaskRedis):
            raise ValueError(FlaskRedis)

    def __getitem__(self, name):
        return self.__client.get(name)

    def __setitem__(self, name, value):
        self.__client.set(name, value)

    def mset(self, nvs):
        """ 批量设置
        """
        self.__client.mset(nvs)


class GlobalCache(object):
    """ 创建一个唯一的全局 Cache 方便使用
    注意这个全局代表同进程全局，因此在使用 DictCache 和 UwsgiCache 的时候，需要自行同步
    """
    def __init__(self, cache):
        self.cache = cache

    @classmethod
    def from_config(cls, ctype, **kwargs):
        """ 获取一个 Cache 实例
        """
        warnings.warn('USE CACHE {}'.format(ctype))
        if ctype == 'uwsgi':
            return cls(UwsgiCache())
        elif ctype == 'redis':
            return cls(RedisCache(kwargs.get('flask_redis_client')))
        return cls(DictCache())

    @property
    def ctype(self):
        return self.cache.ctype

    def keyname(self, r, name):
        return str(r) + '_' + str(name)

    def getg(self, name, r=0):
        """ 默认使用 0 这个r值，代表不区分 r
        """
        if r is None or name is None:
            return None
        return self.cache[self.keyname(r, name)]

    def setg(self, name, value, r=0):
        """ 默认使用 0 这个r值，代表不区分 r
        """
        if r is not None and name is not None and value is not None:
            self.cache[self.keyname(r, name)] = value

    def msetg(self, nvs, r=0):
        """ 设置一组缓存
        """
        # 若提供了 setall 方法则直接调用
        newkey_nvs = {}
        for n, v in nvs.items():
            newkey_nvs[self.keyname(r, n)] = v
        if getattr(self.cache, 'mset', None):
            self.cache.mset(newkey_nvs)
        else:
            for n2, v2 in newkey_nvs.items():
                self.cache[n2] = v2

    def delg(self, name, r=0):
        """ 默认使用 0 这个r值，代表不区分 r
        """
        if r is not None and name is not None:
            self.cache[self.keyname(r, name)] = None
