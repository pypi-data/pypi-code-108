# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/24 7:34 下午
# Copyright (C) 2021 The lesscode Team

from tornado.options import options, define

from lesscode.db.connection_info import ConnectionInfo
from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode

define("database", default={}, type=dict, help="数据库链接资源池,内部使用")
define("conn_info", default=None, type=list, help="数据库链接信息")


class InitConnectionPool:
    """
    初始化连接池
    """

    @staticmethod
    async def create_pool():
        """
        获取配置的链接信息，生成对应的连接池
        :return:
        """
        if options.conn_info:
            for conn_info in options.conn_info:
                if conn_info.enable:
                    if options.database.keys().__contains__(conn_info.name):
                        # 相同key的连接池已经存在，抛出异常
                        raise BusinessException(StatusCode.RESOURCE_EXIST(f"{conn_info.name}连接池"))
                    pool = None
                    # 依据数据库类型进行链接池创建
                    if conn_info.dialect == "postgresql":
                        pool = await InitConnectionPool.create_pool_postgresql(conn_info)
                    elif conn_info.dialect == "mysql":
                        pool = await InitConnectionPool.create_pool_mysql(conn_info)
                    elif conn_info.dialect == "mongodb":
                        pool = InitConnectionPool.create_pool_mongodb(conn_info)
                    elif conn_info.dialect == "elasticsearch":
                        pool = await InitConnectionPool.create_pool_es(conn_info)
                    if pool:
                        options.database[conn_info.name] = (pool, conn_info.dialect)

    @staticmethod
    async def create_pool_postgresql(conn_info: ConnectionInfo):
        """
        创建postgresql 异步连接池
        :param conn_info: 连接信息
        :return: AsyncConnectionPool
        """
        if conn_info.async_enable:
            from aiopg import create_pool
            pool = await create_pool(host=conn_info.host, port=conn_info.port, user=conn_info.user,
                                     password=conn_info.password,
                                     database=conn_info.db_name)
            return pool
        else:
            raise NotImplementedError

    @staticmethod
    async def create_pool_mysql(conn_info: ConnectionInfo):
        """
        创建mysql 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        if conn_info.async_enable:
            import aiomysql
            pool = await aiomysql.create_pool(host=conn_info.host, port=conn_info.port, user=conn_info.user,
                                              password=conn_info.password,
                                              db=conn_info.db_name, autocommit=True, minsize=conn_info.min_size,
                                              maxsize=conn_info.max_size)
            return pool
        else:
            raise NotImplementedError

    @staticmethod
    def create_pool_mongodb(conn_info: ConnectionInfo):
        """
        创建mongodb 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        if conn_info.async_enable:
            import motor
            conn_info_string = f"mongodb://{conn_info.user}:{conn_info.password}@{conn_info.host}:{conn_info.port}"
            if conn_info.params:
                if conn_info.params == "LDAP":
                    conn_info_string += "/?authMechanism=PLAIN"
                elif conn_info.params == "Password":
                    conn_info_string += "/?authSource=admin"
                elif conn_info.params == "X509":
                    conn_info_string += "/?authMechanism=MONGODB-X509"
            pool = motor.motor_tornado.MotorClient(conn_info_string)
            return pool
        else:
            raise NotImplementedError

    @staticmethod
    async def create_pool_es(conn_info: ConnectionInfo):
        """
        创建elasticsearch 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        if conn_info.async_enable:
            from elasticsearch import AsyncElasticsearch
            host_str = conn_info.host.split(",")
            hosts = [f"{conn_info.user}:{conn_info.password}@{host}:{conn_info.port}" for host in host_str]
            pool = AsyncElasticsearch(hosts=hosts)
            return pool
        else:
            raise NotImplementedError
