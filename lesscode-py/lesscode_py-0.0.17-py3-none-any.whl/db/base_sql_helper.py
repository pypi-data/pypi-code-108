# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/30 3:27 下午
# Copyright (C) 2021 The lesscode Team
import abc
import logging

from tornado.options import define, options

from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode

define("echo_sql", default=True, type=bool, help="是否启用SQL输出")
define("max_limit", default=500, type=int, help="单次查询最大数量")


class BaseSqlHelper(abc.ABC):
    """
    BaseSqlHelper 是数据操作的基础抽象类，用于定义操作标准接口
    """

    def __init__(self, pool):
        """
        初始化sql工具
        :param pool: 连接池对象
        """
        self.pool = pool

    @abc.abstractmethod
    async def insert_data(self, table_name: str, data):
        """
        对于插入接口的整合，不需要考虑是单条插入还是多条插入，自动区分
        :param table_name:
        :param data:
        :return:
        """
        pass

    @abc.abstractmethod
    async def insert_one_data(self, table_name: str, data: dict):
        """
        新增记录插入
        :param table_name: 表名
        :param data: 待插入数据
        :return:
        """
        pass

    @abc.abstractmethod
    async def insert_many_data(self, table_name: str, data: list):
        """
        批量插入
        :param table_name:
        :param data:
        :return:
        """
        pass

    @abc.abstractmethod
    async def update_data(self, condition_wrapper: ConditionWrapper, param: dict):
        """
        按条件更新
        :param condition_wrapper:
        :param param:
        :return:
        """
        pass

    @abc.abstractmethod
    async def delete_data(self, condition_wrapper: ConditionWrapper):
        """
        按条件删除
        :param condition_wrapper: 删除条件
        :return:
        """
        pass

    @abc.abstractmethod
    async def fetchone_data(self, condition_wrapper: ConditionWrapper):
        """
        查询单条数据
        :param condition_wrapper: 查询条件信息
        :return:
        """
        pass

    @abc.abstractmethod
    async def fetchall_data(self, condition_wrapper: ConditionWrapper):
        """
        查询多条数据
        :param condition_wrapper: 查询条件信息
        :return:
        """
        pass

    @abc.abstractmethod
    async def fetchall_page(self, condition_wrapper: ConditionWrapper, page_num=1, page_size=10):
        """
        分页查询多条数据
        :param condition_wrapper: 查询条件信息，不含分页信息
        :param page_num: 当前页码
        :param page_size: 每页数量
        :return:
        """
        pass

    @abc.abstractmethod
    async def execute_sql(self, sql: str, param=None):
        """
        执行sql 仅返回影响数量
        :param sql:
        :param param:
        :return:
        """
        pass

    @abc.abstractmethod
    async def executemany_sql(self, sql: str, param=None):
        """
        执行批量sql 仅返回影响数量
        :param sql:
        :param param:
        :return:
        """
        pass

    @abc.abstractmethod
    async def execute_fetchone(self, sql: str, param=None):
        """
        查询单条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        pass

    @abc.abstractmethod
    async def execute_fetchall(self, sql: str, param=None):
        """
        查询多条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        pass

    @abc.abstractmethod
    def prepare_insert_sql(self, table_name: str, item: dict):
        """
        组装插入sql
        :param table_name:
        :param item:
        :return:
        """
        pass

    @abc.abstractmethod
    def prepare_update_sql(self, condition_wrapper: ConditionWrapper, param: dict):
        """
        组装更新sql
        :param condition_wrapper:
        :param param:
        :return:
        """
        pass

    @abc.abstractmethod
    def prepare_delete_sql(self, condition_wrapper: ConditionWrapper):
        """
        组装删除SQl
        :param condition_wrapper:
        :return:
        """
        pass

    @abc.abstractmethod
    def prepare_condition_sql(self, conditions: list):
        """
        拼接条件SQL 搜集参数信息
        :param conditions: 条件信息
        :return: 条件sql片段, values 对应参数
        """
        pass

    @abc.abstractmethod
    def prepare_query_sql(self, condition_wrapper: ConditionWrapper):
        """
        获取完整拼接查询SQL
        :param condition_wrapper: 查询条件对象
        :return:sql 查询sql, values 对应参数
        """
        pass

    @abc.abstractmethod
    def prepare_page_sql(self, condition_wrapper: ConditionWrapper, page_num: int, page_size: int):
        """
        获取分页SQL
        :param condition_wrapper: 查询参数
        :param page_num: 当前页
        :param page_size: 每页记录数
        :return:page_sql 分页sql, values 对应参数, count_sql 统计总数sql
        """
        pass

    @staticmethod
    def dict_row(desc, values):
        """
        记录解析方法
        :param desc:
        :param values:
        :return:
        """
        if desc is None:
            raise BusinessException(StatusCode.INTERNAL_SERVER_ERROR("没有需要解析的结果集"))
        titles = [c[0] for c in desc]
        if isinstance(values, list):
            return [dict(zip(titles, value)) for value in values]
        elif isinstance(values, tuple):
            return dict(zip(titles, values))


def echo_sql(func):
    """
    输出执行SQL的装饰器，要求方法 第一个是SQL 第二个是参数
    :param func:
    :return:
    """

    def wrapper(self, *args, **kwargs):
        if options.echo_sql:
            if len(args) > 1:
                logging.info(f"SQL：{str(args[0])}；参数：{str(args[1:])}")
            else:
                logging.info(f"SQL：{str(args[0])}")
        return func(self, *args, **kwargs)

    return wrapper
