# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/26 3:56 下午
# Copyright (C) 2021 The lesscode Team

from tornado.options import options

from lesscode.db.elasticsearch_helper import ElasticsearchHelper
from lesscode.db.mongodb_helper import MongodbHelper
from lesscode.db.mysql_helper import MysqlHelper
from lesscode.db.base_sql_helper import BaseSqlHelper
from lesscode.db.postgresql_helper import PostgresqlHelper
from lesscode.db.condition_wrapper import ConditionWrapper


class DSHelper(BaseSqlHelper):
    """
    对外暴露的工具类，对数据库操作采用代理模式进行了包装
    """

    def __init__(self, pool_name):
        """
        初始化sql工具
        :param pool_name: 连接池名称
        """
        self.pool, self.dialect = options.database[pool_name]
        if self.dialect == "postgresql":
            self.db_helper = PostgresqlHelper(self.pool)
        elif self.dialect == "mysql":
            self.db_helper = MysqlHelper(self.pool)
        elif self.dialect == "mongodb":
            self.db_helper = MongodbHelper(self.pool)
        elif self.dialect == "elasticsearch":
            self.db_helper = ElasticsearchHelper(self.pool)

    async def insert_data(self, table_name: str, data):
        return await self.db_helper.insert_data(table_name, data)

    async def insert_one_data(self, table_name: str, data: dict):
        return await self.db_helper.insert_one_data(table_name, data)

    async def insert_many_data(self, table_name: str, data: list):
        return await self.db_helper.insert_many_data(table_name, data)

    async def update_data(self, condition_wrapper: ConditionWrapper, param: dict):
        return await self.db_helper.update_data(condition_wrapper, param)

    async def delete_data(self, condition_wrapper: ConditionWrapper):
        return await self.db_helper.delete_data(condition_wrapper)

    async def fetchone_data(self, condition_wrapper: ConditionWrapper):
        return await self.db_helper.fetchone_data(condition_wrapper)

    async def fetchall_data(self, condition_wrapper: ConditionWrapper):
        return await self.db_helper.fetchall_data(condition_wrapper)

    async def fetchall_page(self, condition_wrapper: ConditionWrapper, page_num=1, page_size=10):
        return await self.db_helper.fetchall_page(condition_wrapper, page_num, page_size)

    async def execute_sql(self, sql: str, param=None):
        return await self.db_helper.execute_sql(sql, param)

    async def executemany_sql(self, sql: str, param=None):
        return await self.db_helper.executemany_sql(sql, param)

    async def execute_fetchone(self, sql: str, param=None):
        return await self.db_helper.execute_fetchone(sql, param)

    async def execute_fetchall(self, sql: str, param=None):
        return await self.db_helper.execute_fetchall(sql, param)

    def prepare_insert_sql(self, table_name: str, item: dict):
        return self.db_helper.prepare_insert_sql(table_name, item)

    def prepare_update_sql(self, condition_wrapper: ConditionWrapper, param: dict):
        return self.db_helper.prepare_update_sql(condition_wrapper, param)

    def prepare_delete_sql(self, condition_wrapper: ConditionWrapper):
        return self.db_helper.prepare_delete_sql(condition_wrapper)

    def prepare_condition_sql(self, conditions: list):
        return self.db_helper.prepare_condition_sql(conditions)

    def prepare_query_sql(self, condition_wrapper: ConditionWrapper):
        return self.db_helper.prepare_query_sql(condition_wrapper)

    def prepare_page_sql(self, condition_wrapper: ConditionWrapper, page_num: int, page_size: int):
        return self.db_helper.prepare_page_sql(condition_wrapper, page_num, page_size)
