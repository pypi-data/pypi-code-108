# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/12/8 10:53 上午
# Copyright (C) 2021 The lesscode Team
import logging
from tornado.options import options
from lesscode.db.base_sql_helper import BaseSqlHelper, echo_sql
from lesscode.db.condition_wrapper import ConditionWrapper
from lesscode.db.page import Page
from lesscode.utils.aes import AES


class ElasticsearchHelper(BaseSqlHelper):
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

    async def fetchone_data(self, condition_wrapper: ConditionWrapper, aes_enable=True, aes_key=None):
        """
        查询单条数据
        :param aes_key: aes加密的key
        :param aes_enable: aes加密开关
        :param condition_wrapper:  查询条件信息
        :return:
        """
        table_str = condition_wrapper.table
        aggregate = self.prepare_query_sql(condition_wrapper)
        return await self.execute_fetchone(table_str, aggregate.get("$match", []), aes_enable=aes_enable,
                                           aes_key=aes_key)

    async def fetchall_data(self, condition_wrapper: ConditionWrapper, aes_enable=True, aes_key=None):
        """
        查询多条数据
        :param aes_key: aes加密的key
        :param aes_enable: aes加密开关
        :param condition_wrapper: 查询条件信息
        :return:
        """
        table_str = condition_wrapper.table
        aggregate = self.prepare_query_sql(condition_wrapper)
        rs = await self.execute_fetchall(table_str, aggregate.get("$match", []), column=aggregate.get("includes", []),
                                         aes_enable=aes_enable, aes_key=aes_key)
        return rs

    async def fetchall_page(self, condition_wrapper: ConditionWrapper, page_num=1, page_size=10, aes_enable=True,
                            aes_key=None):
        """
        分页查询多条数据
        :param aes_key: aes加密的key
        :param aes_enable: aes加密开关
        :param condition_wrapper:
        :param page_num: 当前页码
        :param page_size: 每页数量
        :return:
        """
        table_str = condition_wrapper.table
        aggregate = self.prepare_page_sql(condition_wrapper, page_num, page_size)
        orders = []
        for od in aggregate.get("sort", []):
            for x in od:
                order_type = od.get(x, {}).get("order")
                if order_type in ["ASC", "DESC"]:
                    order_type = order_type.lower()
                else:
                    order_type = "asc"
                orders.append({x: {"order": order_type}})
        records = await self.execute_fetch(table_str, aggregate.get("$match", []), offset=(page_num - 1) * page_size,
                                           size=page_size, column=aggregate.get("includes", []), sort=orders,
                                           aes_enable=aes_enable, aes_key=aes_key)
        total = await self.execute_count(table_str, aggregate.get("$match", []))
        return Page(records=records, current=page_num, page_size=page_size, total=total.get("count", 0)).__dict__

    @echo_sql
    async def execute_fetchone(self, param=None, sql: list = [], column: list = [], aes_enable=True, aes_key=None):
        """
        查询单条数据
        :param aes_key: aes密钥
        :param aes_enable: 是否开启aes加密
        :param column: 返回的字段
        :param sql: 待执行的Sql语句
        :param param: 表名
        :return:
        """

        body = {
            "query": {
                "bool": {
                    "must": sql
                }
            },
            "size": 1
        }
        resp = await self.pool.search(
            index=param,
            body=body,
            _source_includes=column
        )
        hits = resp.get("hits", {}).get("hits", [])
        if hits:
            info = hits[0].get("_source", {})
            info.update({"_id": hits[0].get("_id")})
            if aes_enable:
                key = "haohaoxuexi"
                if aes_key:
                    key = aes_key
                info["_id"] = AES.encrypt(key, info.get("_id"))
            return info
        return None

    @echo_sql
    async def execute_fetchall(self, param: str, sql: list = [], column: list = [], scroll: str = "5m",
                               size: int = 100, timeout: str = "3s", sort: list = [], aes_enable=True, aes_key=None):
        """
        查询多条数据
        :param sort: 排序
        :param aes_key: aes密钥
        :param aes_enable: 是否开启aes加密
        :param column: 返回的字段
        :param timeout: 超时时间
        :param size: 数据数量
        :param scroll: 滚动时间
        :param sql: 待执行的Sql语句
        :param param: 表名
        :return:
        """
        body = {
            "query": {
                "bool": {
                    "must": sql
                }
            }
        }
        if sort:
            body["sort"] = sort
        resp = await self.pool.search(
            index=param,
            body=body,
            _source_includes=column,
            scroll=scroll,
            timeout=timeout,
            size=size
        )
        hits = resp.get("hits", {}).get("hits", [])
        records = []
        if hits:
            scroll_id = resp.get("_scroll_id")
            while True:
                rt = await self.pool.scroll(scroll_id=scroll_id, scroll=scroll)
                new_hits = rt.get("hits", {}).get("hits", [])
                if new_hits:
                    hits += new_hits
                else:
                    break
            for x in hits:
                info = x.get("_source", {})
                info.update({"_id": x.get("_id")})
                if aes_enable:
                    key = "haohaoxuexi"
                    if aes_key:
                        key = aes_key
                    info["_id"] = AES.encrypt(key, info.get("_id"))
                records.append(info)
        return records

    @echo_sql
    async def execute_fetch(self, param: str, sql: list = [], column: list = None, offset=0,
                            size=100, sort: list = [], aes_enable=True, aes_key=None):
        """
        查询多条数据
        :param sort: 排序
        :param aes_key: aes密钥
        :param aes_enable: 是否开启aes加密
        :param size: 数据量
        :param offset: 偏移量
        :param column: 返回值的字段
        :param sql: 待执行的Sql语句
        :param param: 表名
        :return:
        """
        body = {
            "query": {
                "bool": {
                    "must": sql
                }
            },
            "from": offset,
            "size": size
        }
        if sort:
            body["sort"] = sort
        resp = await self.pool.search(
            index=param,
            body=body,
            _source_includes=column
        )
        hits = resp.get("hits", {}).get("hits", [])
        records = []
        for x in hits:
            info = x.get("_source", {})
            info.update({"_id": x.get("_id")})
            if aes_enable:
                key = "haohaoxuexi"
                if aes_key:
                    key = aes_key
                info["_id"] = AES.encrypt(key, info.get("_id"))
            records.append(info)
        return records

    @echo_sql
    async def execute_count(self, param: str, sql: list = []):
        """
        查询多条数据
        :param sql: 待执行的Sql语句
        :param param: 表名
        :return:
        """
        body = {
            "query": {
                "bool": {
                    "must": sql
                }
            }
        }
        resp = await self.pool.count(
            index=param,
            body=body
        )
        return resp

    @echo_sql
    async def execute_group(self, param: str, sql: list = [], groups: list = []):
        """
        查询多条数据
        :param groups: 分组字段列表
        :param sql: 待执行的Sql语句
        :param param: 表名
        :return:
        """
        body = {
            "query": {
                "bool": {
                    "must": sql
                }
            }
        }
        key = {}
        if groups:
            for g in groups[::-1]:
                ix = groups.index(g)
                if ix < len(groups):
                    terms = {"terms": {"field": g, "size": 65535}}
                    if key:
                        key = {"aggs": {str(ix): terms, "aggs": key.get("aggs", {})}}
                    else:
                        key = {"aggs": {str(ix): terms}}
        if key:
            body["size"] = 0
            body.update(key)
        resp = await self.pool.search(
            index=param,
            body=body
        )
        return resp

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
        operators = ["AND"]
        if len(conditions) == 0:
            return {}
        filter_item = []
        first_filter_items = {"bool": {"must": []}}
        for condition in conditions:
            # 获取当前过滤条件
            operator, column, value = condition
            if operator in ["OR", "AND"]:
                if operator == "AND":
                    operators.append("AND")
                    first_filter_items = {"bool": {"must": []}}
                elif operator == "OR":
                    operators.append("OR")
                    first_filter_items = {"bool": {"should": []}}
                continue
            if operator == "=":
                condition_item = {"term": {column: value}}
            elif operator == "<>":
                condition_item = {"must_not": {"term": {column: value}}}
            elif operator == ">":
                condition_item = {"range": {column: {"gt": value}}}
            elif operator == ">=":
                condition_item = {"range": {column: {"gte": value}}}
            elif operator == "<":
                condition_item = {"range": {column: {"lt": value}}}
            elif operator == "<=":
                condition_item = {"range": {column: {"lte": value}}}
            elif operator == "BETWEEN":
                # 大于等于小数 小于 大数
                condition_item = {"range": {column: {"gte": value[0], "lt": value[1]}}}
            elif operator == "NOT_BETWEEN":
                # 小于小数  大于等于大数
                condition_item = {"$and": [{column: {"$lt": value[0]}}, {column: {"$gte": value[1]}}]}
            elif operator == "LIKE":
                condition_item = {"match_phrase": {column: value}}
            elif operator == "NOT_LIKE":
                condition_item = {"must_not": {"match_phrase": {column: value}}}
            elif operator == "LIKE_LEFT":
                condition_item = {"prefix": {column: {"value": value}}}
            elif operator == "LIKE_RIGHT":
                condition_item = {column: {"$regex": f".*{value}$", "$options": "$i"}}
            elif operator == "IS_NULL":
                condition_item = {column: None}
            elif operator == "IS_NOT_NULL":
                condition_item = {column: {"$ne": None}}
            elif operator == "IN":
                condition_item = {"terms": {column: value}}
            elif operator == "NOT_IN":
                condition_item = {"must_not": {"terms": {column: value}}}
            else:
                continue
            if operators[-1] == "OR":
                first_filter_items["bool"]["should"].append(condition_item)
            elif operators[-1] == "AND":
                first_filter_items["bool"]["must"].append(condition_item)
            else:
                continue
        filter_item.append(first_filter_items)
        logging.debug(f"Elasticsearch Condition:{filter_item}")
        return filter_item

    def prepare_query_sql(self, condition_wrapper: ConditionWrapper):
        """
        获取完整拼接查询SQL
        :param condition_wrapper: 查询条件对象
        :return:查询对象，分组对象，排序对象
        """
        aggregate = {"includes": condition_wrapper.column}
        # 聚合参数
        if condition_wrapper.conditions:
            filter_items = self.prepare_condition_sql(condition_wrapper.conditions)
            aggregate.update({"$match": filter_items})
        # 拼接 分组SQL
        if condition_wrapper.groups:
            aggregate.update({"$group": condition_wrapper.groups})
        # 拼接 排序SQL
        if condition_wrapper.order:
            order_item = []
            for order in condition_wrapper.order:
                column, op = order
                order_item.append({column: {"order": op, "missing": "_last"}})
            aggregate["sort"] = order_item
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
            aggregate = {}
        # 组装查询数量语句
        # 组装分页
        aggregate.update({"from": Page.skip(page_num, page_size)})
        aggregate.update({"size": int(page_size)})
        return aggregate

    async def execute_sql(self, sql: str, param=None):
        pass

    async def executemany_sql(self, sql: str, param=None):
        pass
