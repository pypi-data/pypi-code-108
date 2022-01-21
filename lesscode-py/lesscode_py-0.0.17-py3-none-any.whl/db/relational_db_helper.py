# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/12/3 2:19 下午
# Copyright (C) 2021 The lesscode Team
from abc import ABC

from lesscode.db.base_sql_helper import BaseSqlHelper
from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.db.db_function import DBFunction
from lesscode.db.page import Page


class RelationalDbHelper(BaseSqlHelper, ABC):
    """
    RelationalDbHelper 对关系型数据库操作进行默认实现
    """

    async def insert_data(self, table_name: str, data):
        """
        对于插入接口的整合，不需要考虑是单条插入还是多条插入，自动区分
        :param table_name:
        :param data:
        :return:
        """
        if isinstance(data, list):
            if len(data) == 1:
                return await self.insert_one_data(table_name, data[0])
            else:
                return await self.insert_many_data(table_name, data)
        elif isinstance(data, dict):
            return await self.insert_one_data(table_name, data)

    async def insert_one_data(self, table_name: str, data: dict):
        """
        新增记录插入
        :param table_name: 表名
        :param data: 待插入数据
        :return:
        """
        insert_sql = self.prepare_insert_sql(table_name, data)
        param = []
        for v in data.values():
            if isinstance(v, DBFunction):
                param.append(v.value)
            else:
                param.append(v)
        rs = await self.execute_sql(insert_sql, param)
        return rs

    async def insert_many_data(self, table_name: str, data: list):
        """
        批量插入
        :param table_name:
        :param data:
        :return:
        """
        insert_sql = self.prepare_insert_sql(table_name, data.__getitem__(0))
        return await self.executemany_sql(insert_sql, data)

    async def update_data(self, condition_wrapper: ConditionWrapper, data: dict):
        """
        按条件更新
        :param condition_wrapper: 更新条件
        :param data:更新值
        :return:
        """
        update_sql, values = self.prepare_update_sql(condition_wrapper, data)
        rs = await self.execute_sql(update_sql, values)
        return rs

    async def delete_data(self, condition_wrapper: ConditionWrapper):
        """
        按条件删除
        :param condition_wrapper: 删除条件
        :return:
        """
        delete_sql, values = self.prepare_delete_sql(condition_wrapper)
        rs = await self.execute_sql(delete_sql, values)
        return rs

    async def fetchone_data(self, condition_wrapper: ConditionWrapper):
        """
        查询单条数据
        :param condition_wrapper:  查询条件信息
        :return:
        """
        query_sql, values = self.prepare_query_sql(condition_wrapper)
        return await self.execute_fetchone(query_sql, values)

    async def fetchall_data(self, condition_wrapper: ConditionWrapper):
        """
        查询多条数据
        :param condition_wrapper: 查询条件信息
        :return:
        """
        query_sql, values = self.prepare_query_sql(condition_wrapper)
        return await self.execute_fetchall(query_sql, values)

    async def fetchall_page(self, condition_wrapper: ConditionWrapper, page_num=1, page_size=10):
        """
        分页查询多条数据
        :param condition_wrapper:
        :param page_num: 当前页码
        :param page_size: 每页数量
        :return:
        """
        page_sql, values, count_sql = self.prepare_page_sql(condition_wrapper, page_num, page_size)
        # 查询分页记录
        records = await self.execute_fetchall(page_sql, values)
        # 查询记录数量
        total = await self.execute_fetchone(count_sql, values)
        # 组装成page包装类 最终转为 dict 类型 为转换json
        return Page(records=records, current=page_num, page_size=page_size, total=total.get("total")).__dict__

    def prepare_insert_sql(self, table_name: str, item: dict):
        """
        组装插入sql
        :param table_name:
        :param item:
        :return:
        """
        # 组装插入数据字段
        column_str = ','.join(item.keys())
        # 依据字段数组织占位符
        # placeholder_str = ','.join('%s' for v in range(len(item)))
        placeholder_items = []
        for v in item.values():
            if isinstance(v,DBFunction):
                placeholder_items.append(v.function_body)
            else:
                placeholder_items.append("%s")
        placeholder_str = ','.join(placeholder_items)
        # 组装可执行SQL
        insert_sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholder_str})"
        return insert_sql

    def prepare_update_sql(self, condition_wrapper: ConditionWrapper, param: dict):
        """
        组装更新sql
        :param condition_wrapper:
        :param param:
        :return:
        """
        # column_sql = ','.join(f"{key}=%s" for key in param.keys())
        value_items = []
        placeholder_items = []
        for key in param.keys():
            v = param.get(key)
            if isinstance(v, DBFunction):
                placeholder_items.append(f"{key}={v.function_body}")
                value_items.append(v.value)
            else:
                placeholder_items.append(f"{key}=%s")
                value_items.append(v)
        column_sql = ','.join(placeholder_items)
        condition_sql, values = self.prepare_condition_sql(condition_wrapper.conditions)
        update_sql = f"UPDATE {condition_wrapper.table} SET {column_sql} WHERE {condition_sql}"
        return update_sql, value_items+values

    def prepare_delete_sql(self, condition_wrapper: ConditionWrapper):
        """
        组装删除SQl
        :param condition_wrapper:
        :return:
        """
        condition_sql, values = self.prepare_condition_sql(condition_wrapper.conditions)
        delete_sql = f"DELETE FROM {condition_wrapper.table} WHERE {condition_sql}"
        return delete_sql, values

    def prepare_condition_sql(self, conditions: list):
        """
        拼接条件SQL 搜集参数信息
        :param conditions: 条件信息
        :return: 条件sql片段, values 对应参数
        """
        connector = "AND"
        condition_sql = ""
        values = []
        for condition in conditions:
            operator, column, value = condition
            if operator == "OR" or operator == "AND":
                connector = operator
                continue
            if operator == "BETWEEN":
                sql_segment = f"{column} BETWEEN %s AND %s"
            elif operator == "NOT_BETWEEN":
                sql_segment = f"{column} NOT BETWEEN %s AND %s"
            elif operator == "LIKE":
                sql_segment = f"{column} LIKE %s"
                value = f"%{value}%"
            elif operator == "NOT_LIKE":
                sql_segment = f"{column} NOT_LIKE %s"
                value = f"%{value}%"
            elif operator == "LIKE_LEFT":
                sql_segment = f"{column} LIKE %s"
                value = f"%{value}"
            elif operator == "LIKE_RIGHT":
                sql_segment = f"{column} LIKE %s"
                value = f"{value}%"
            elif operator == "IS_NULL":
                sql_segment = f"{column} IS NULL "
            elif operator == "IS_NOT_NULL":
                sql_segment = f"{column} IS NOT NULL "
            elif operator == "IN":
                # 依据字段数组织占位符
                placeholder_str = ','.join('%s' for v in range(len(value)))
                sql_segment = f"{column} IN ({placeholder_str})"
            elif operator == "NOT_IN":
                # 依据字段数组织占位符
                placeholder_str = ','.join('%s' for v in range(len(value)))
                sql_segment = f"{column} NOT IN ({placeholder_str})"
            else:
                # 操作符号不需要转码的
                sql_segment = f"{column} {operator} %s"
            if condition_sql:
                condition_sql = f"{condition_sql} {connector} {sql_segment}"
            else:
                condition_sql = sql_segment
            if column is not None:
                if isinstance(value, list):
                    values.extend(value)
                else:
                    values.append(value)
        return condition_sql, values

    def prepare_query_sql(self, condition_wrapper: ConditionWrapper):
        """
                获取完整拼接查询SQL
                :param condition_wrapper: 查询条件对象
                :return:sql 查询sql, values 对应参数
                """
        sql = f"SELECT {','.join(condition_wrapper.column)} FROM {condition_wrapper.table} "
        condition_sql, values = self.prepare_condition_sql(condition_wrapper.conditions)
        # 拼接 条件SQL
        if condition_sql:
            sql += f" WHERE {condition_sql}"
        # 拼接 分组SQL
        if condition_wrapper.group:
            group_sql = ""
            if isinstance(condition_wrapper.group, str):
                group_sql = f" GROUP BY {condition_wrapper.group}"
            elif isinstance(condition_wrapper.group, list):
                group_sql = f" GROUP BY {','.join(condition_wrapper.group)}"
            sql += group_sql
        # 拼接 排序SQL
        if condition_wrapper.order:
            sql += f" ORDER BY {','.join([' '.join(item) for item in condition_wrapper.order])}"
        return sql, values

    def prepare_page_sql(self, condition_wrapper: ConditionWrapper, page_num: int, page_size: int):
        """
        获取分页SQL
        :param condition_wrapper: 查询参数
        :param page_num: 当前页
        :param page_size: 每页记录数
        :return:page_sql 分页sql, values 对应参数, count_sql 统计总数sql
        """
        query_sql, values = self.prepare_query_sql(condition_wrapper)
        cols = []
        for col in condition_wrapper.column:
            col = col.upper().replace("AS", "").strip().split(" ")
            cols.append(col[-1].strip())
        # 组装分页查询语句，需要依据页码计算 起始索引
        page_sql = f"SELECT {','.join(cols)} FROM ({query_sql}) cs OFFSET {Page.skip(page_num,page_size)} LIMIT {page_size}"
        # 组装查询数量语句
        count_sql = f"SELECT count(1) total FROM ({query_sql}) cs"
        return page_sql, values, count_sql



