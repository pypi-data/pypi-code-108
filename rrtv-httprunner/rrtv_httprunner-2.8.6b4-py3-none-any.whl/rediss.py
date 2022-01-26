# @author: chenfanghang
import json
from typing import Union, Text, Dict

import redis
from loguru import logger
from rrtv_httprunner import exceptions


class RedisHandler:
    def __init__(self, driver: Union[Text, Dict]):
        if driver is None:
            raise exceptions.DBError("redis datasource not configured")
        driver = driver if isinstance(driver, dict) else eval(driver)
        try:
            self.r = redis.Redis(host=str(driver["host"] if "host" in driver else driver["hostName"]),
                                 password=driver["password"], port=int(driver["port"]),
                                 db=driver["db"] if "db" in driver else driver["database"])  # 连接redis固定方法,这里的值必须固定写死
        except Exception as e:
            logger.error("redis连接失败，错误信息:%s" % e)
            raise exceptions.DBConnectionError("redis连接失败，错误信息:%s" % e)

    def command(self):
        return self.r

    def exists(self, key):
        return self.r.exists(key)

    def str_get(self, k):
        res = self.r.get(k)  # 会从服务器传对应的值过来，性能慢
        if res:
            return res.decode()  # 从redis里面拿到的是bytes类型的数据，需要转换一下

    def str_set(self, k, v, ex=None):  # time默认失效时间
        if isinstance(v, Dict):
            self.r.set(k, json.dumps(v), ex=ex)
        else:
            self.r.set(k, v, ex=ex)

    def delete(self, k):
        tag = self.r.exists(k)
        # 判断这个key是否存在,相对于get到这个key他只是传回一个存在火灾不存在的信息，
        # 而不用将整个k值传过来（如果k里面存的东西比较多，那么传输很耗时）
        if tag:
            self.r.delete(k)
            return 1
        else:
            logger.debug(f"{k}:传入的key不存在")
            return 0

    def hash_get(self, name, k):  # 哈希类型存储的是多层字典（嵌套字典）
        res = self.r.hget(name, k)
        if res:
            return res.decode()  # 因为get不到值得话也不会报错所以需要判断一下

    def hash_set(self, name, k, v):  # 哈希类型的是多层
        self.r.hset(name, k, v)  # set也不会报错

    def hash_hkeys(self, name):  # 哈希类型，获取所有的key
        return self.r.hkeys(name)

    def hash_getall(self, name):
        res = self.r.hgetall(name)  # 得到的是字典类型的，里面的k,v都是bytes类型的
        data = {}
        if res:
            for k, v in res.items():  # 循环取出字典里面的k,v，在进行decode
                k = k.decode()
                v = v.decode()
                data[k] = v
        return data

    def hash_del(self, name, k):
        res = self.r.hdel(name, k)
        if res:
            return 1
        else:
            logger.debug(f"{name, k} 删除失败，该key不存在")
            return 0

    """
    set 基本命令封装

    """

    def sadd(self, name, values):
        """Add ``value(s)`` to set ``name``
        sadd myZSet zlh
        添加分数为1，值为zlh的zset集合
        """
        return self.r.sadd(name, values)

    def scard(self, name):
        "Return the number of elements in set ``name``"
        return self.r.scard(name)

    def sismember(self, name, value):
        "Return a boolean indicating if ``value`` is a member of set ``name``"
        return self.r.sismember(name, value)

    def smembers(self, name):
        "Return all members of the set ``name``"
        return self.r.smembers(name)

    def smove(self, src, dst, value):
        "Move ``value`` from set ``src`` to set ``dst`` atomically"
        return self.r.smove(src, dst, value)

    def spop(self, name, count=None):
        "Remove and return a random member of set ``name``"
        args = (count is not None) and [count] or []
        return self.r.spop(name, args)

    def srem(self, name, values):
        "Remove ``values`` from set ``name``"
        return self.r.srem(name, values)

    """
    zset 基本命令
    """

    # def zadd(self, name, mapping):
    #     return self.r.zadd(name, values)
    def zcard(self, name):
        "Return the number of elements in the sorted set ``name``"
        return self.r.zcard(name)

    def zcount(self, name, min, max):
        """
        Returns the number of elements in the sorted set at key ``name`` with
        a score between ``min`` and ``max``.
        """
        return self.r.zcount(name, min, max)

    def zrangebyscore(self, name, min, max):
        """
        zset 显示所有成员

        """
        return self.r.zrangebyscore(name, min, max)

    """
      list 基本命令封装

    """

    def brpop(self, keys):
        """list 右边删除一个元素"""
        logger.debug(f'RedisHandler brpop的 key为:{keys}')
        self.r.brpop(keys)

    def lpop(self, keys):
        """list 左边删除一个元素"""
        logger.debug(f'RedisHandler lpop的 key为:{keys}')
        self.r.lpop(keys)

    def lpush(self, name, value):
        """list 左边添加一个元素"""
        logger.debug(f'RedisHandler lpush的name为:{name} key为{value}')
        self.r.lpush(name, value)

    def lrange(self, name, start, end):
        """list 列表指定返回的长度"""
        logger.debug(f'RedisHandler lrange的name为:{name} start为{start} end为{end}')
        self.r.lrange(name, start, end)

    def lrem(self, name, count, value):
        """list 删除指定长的的元素"""
        logger.debug(f'RedisHandler lrange的name为:{name} count为{count} value为{value}')
        self.r.lrange(name, count, value)


    @property  # 属性方法，
    def clean_redis(self):
        self.r.flushdb()  # 清空 redis
        logger.debug("清空redis成功！")
        return 0
