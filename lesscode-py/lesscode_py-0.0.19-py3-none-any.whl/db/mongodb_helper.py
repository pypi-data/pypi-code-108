# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/12/3 2:19 下午
# Copyright (C) 2021 The lesscode Team
import logging
from tornado.options import options
from lesscode.db.base_sql_helper import BaseSqlHelper, echo_sql
from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.db.page import Page


class MongodbHelper(BaseSqlHelper):
    """
    MongodbHelper  Mongodb数据库操作实现
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
        db_str, collection_str = table_name.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        await collection.insert_one(data)
        return {"rowcount": 1}

    async def insert_many_data(self, table_name: str, data: list):
        """
        批量插入
        :param table_name:
        :param data:
        :return:
        """
        db_str, collection_str = table_name.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        rs = await collection.insert_many(data)
        return {"rowcount": len(rs.inserted_ids)}

    async def update_data(self, condition_wrapper: ConditionWrapper, param: dict):
        """
        按条件更新
        :param condition_wrapper: 更新条件
        :param param:更新值
        :return:
        """
        db_str, collection_str = condition_wrapper.table.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        filter_items = self.prepare_condition_sql(condition_wrapper.conditions)
        rs = await collection.update_many(filter_items, {"$set": param})
        return {"rowcount": rs.modified_count}

    async def delete_data(self, condition_wrapper: ConditionWrapper):
        """
        按条件删除
        :param condition_wrapper: 删除条件
        :return:
        """
        db_str, collection_str = condition_wrapper.table.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        filter_items = self.prepare_condition_sql(condition_wrapper.conditions)
        rs = await collection.delete_many(filter_items)
        return {"rowcount": rs.deleted_count}

    async def fetchone_data(self, condition_wrapper: ConditionWrapper):
        """
        查询单条数据
        :param condition_wrapper:  查询条件信息
        :return:
        """
        db_str, collection_str = condition_wrapper.table.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        aggregate = self.prepare_query_sql(condition_wrapper)
        return await self.execute_fetchone(aggregate, {"collection": collection})

    async def fetchall_data(self, condition_wrapper: ConditionWrapper):
        """
        查询多条数据
        :param condition_wrapper: 查询条件信息
        :return:
        """
        db_str, collection_str = condition_wrapper.table.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        aggregate = self.prepare_query_sql(condition_wrapper)
        rs = await self.execute_fetchall(aggregate, {"collection": collection, "length": options.max_limit})
        return rs

    async def fetchall_page(self, condition_wrapper: ConditionWrapper, page_num=1, page_size=10):
        """
        分页查询多条数据
        :param condition_wrapper:
        :param page_num: 当前页码
        :param page_size: 每页数量
        :return:
        """
        db_str, collection_str = condition_wrapper.table.split(".")
        db = self.pool[db_str]
        collection = db[collection_str]
        aggregate, count_ = self.prepare_page_sql(condition_wrapper, page_num, page_size)
        records = await self.execute_fetchall(aggregate, {"collection": collection, "length": int(page_size)})
        # 查询记录数量
        total_result = await self.execute_fetchone(count_, {"collection": collection})
        # 组装成page包装类 最终转为 dict 类型 为转换json
        return Page(records=records, current=page_num, page_size=page_size,
                    total=total_result.get("total", 0) if total_result else 0).__dict__

    @echo_sql
    async def execute_fetchone(self, sql: str, param=None):
        """
        查询单条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        cursor = param["collection"].aggregate(sql)
        rs = await cursor.to_list(1)
        if len(rs) > 0:
            return rs[0]
        return None

    @echo_sql
    async def execute_fetchall(self, sql: str, param=None):
        """
        查询多条数据
        :param sql: 待执行的Sql语句
        :param param: 参数
        :return:
        """
        cursor = param["collection"].aggregate(sql)
        return await cursor.to_list(length=param["length"])

    def prepare_insert_sql(self, table_name: str, item: dict):
        """
        组装插入sql
        :param table_name:
        :param item:
        :return:
        """
        pass

    def prepare_update_sql(self, condition_wrapper: ConditionWrapper, param: dict):
        """
        组装更新sql
        :param condition_wrapper:
        :param param:
        :return:
        """
        pass

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
        connector = "$and"
        if len(conditions) == 0:
            return {}
        filter_item = {"$and": []}
        for condition in conditions:
            # 获取当前过滤条件
            current_filter_items = filter_item.get(connector)
            operator, column, value = condition
            if operator == "OR" or operator == "AND":
                # 当前操作符与连接符不相同，要进行切换
                if connector != operator:
                    connector = "$and" if operator == "AND" else "$or"
                if len(current_filter_items) == 0:
                    # 当前没有过滤条件就重新进行生成，仅发生在第一个条件就直接切换为OR的情况
                    filter_item = {connector: []}
                else:
                    filter_item = {connector: [filter_item]}
                continue
            if operator == "=":
                condition_item = {column: value}
            elif operator == "<>":
                condition_item = {column: {"$ne": value}}
            elif operator == ">":
                condition_item = {column: {"$gt": value}}
            elif operator == ">=":
                condition_item = {column: {"$gte": value}}
            elif operator == "<":
                condition_item = {column: {"$lt": value}}
            elif operator == "<=":
                condition_item = {column: {"$lte": value}}
            elif operator == "BETWEEN":
                # 大于等于小数 小于 大数
                condition_item = {"$and": [{column: {"$gte": value[0]}}, {column: {"$lt": value[1]}}]}
            elif operator == "NOT_BETWEEN":
                # 小于小数  大于等于大数
                condition_item = {"$and": [{column: {"$lt": value[0]}}, {column: {"$gte": value[1]}}]}
            elif operator == "LIKE":
                condition_item = {column: {"$regex": f".*{value}.*", "$options": "$i"}}
            elif operator == "NOT_LIKE":
                condition_item = {column: {"$not": {"$regex": f".*{value}.*", "$options": "$i"}}}
            elif operator == "LIKE_LEFT":
                condition_item = {column: {"$regex": f"^{value}.*", "$options": "$i"}}
            elif operator == "LIKE_RIGHT":
                condition_item = {column: {"$regex": f".*{value}$", "$options": "$i"}}
            elif operator == "IS_NULL":
                condition_item = {column: None}
            elif operator == "IS_NOT_NULL":
                condition_item = {column: {"$ne": None}}
            elif operator == "IN":
                condition_item = {column: {"$in": value}}
            elif operator == "NOT_IN":
                condition_item = {column: {"$nin": value}}
            else:
                continue
            current_filter_items.append(condition_item)
        logging.debug(f"MongoDB Condition:{filter_item}")
        return filter_item

    def prepare_query_sql(self, condition_wrapper: ConditionWrapper):
        """
        获取完整拼接查询SQL
        :param condition_wrapper: 查询条件对象
        :return:查询对象，分组对象，排序对象
        """
        aggregate = []
        # 聚合参数
        if condition_wrapper.conditions:
            filter_items = self.prepare_condition_sql(condition_wrapper.conditions)
            aggregate.append({"$match": filter_items})
        # 拼接 分组SQL
        if condition_wrapper.groups:
            aggregate.append({"$group": condition_wrapper.groups})
        # 拼接 排序SQL
        if condition_wrapper.order:
            order_item = {}
            for order in condition_wrapper.order:
                column, op = order
                order_item.setdefault(column, 1 if op == "ASC" else -1)
            aggregate.append({"$sort": order_item})
        return aggregate

    def prepare_page_sql(self, condition_wrapper: ConditionWrapper, page_num: int, page_size: int):
        """
        获取分页SQL
        :param condition_wrapper: 查询参数
        :param page_num: 当前页
        :param page_size: 每页记录数
        :return:page_sql 分页,  统计总数
        """
        aggregate = self.prepare_query_sql(condition_wrapper)
        if len(aggregate) == 0:
            aggregate = []
        # 组装查询数量语句
        count_ = aggregate.copy()
        count_.append({"$count": 'total'})
        # 组装分页
        aggregate.append({"$skip": Page.skip(page_num, page_size)})
        aggregate.append({"$limit": int(page_size)})
        return aggregate, count_

    async def execute_sql(self, sql: str, param=None):
        pass

    async def executemany_sql(self, sql: str, param=None):
        pass
