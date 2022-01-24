# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2020-08-13 15:06:48
:LastEditors: ChenXiaolei
:Description: redis helper
"""

import redis
from redis import RedisError


class RedisHelper:
    @classmethod
    def redis_init(self, host="", port=0, db=0, password=None, config_dict=None, decode_responses=False):
        """
        :Description: 从redis连接池中创建对象
        :param host:主机地址
        :param port:端口
        :param db:redis_db
        :param password:授权密码
        :return: redis客户端对象
        :last_editors: ChenXiaolei
        """
        if config_dict:
            if "host" in config_dict:
                host = config_dict["host"]
            if "port" in config_dict:
                port = config_dict["port"]
            if "db" in config_dict:
                db = config_dict["db"]
            else:
                db = 0
            if "password" in config_dict:
                password = config_dict["password"]

        if not host or not port or host == "" or int(db) < 0 or int(port) <= 0:
            raise RedisError("Config Value Eroor")

        pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    db=db,
                                    password=password, decode_responses=decode_responses)
        redis_client = redis.Redis(connection_pool=pool)
        return redis_client
