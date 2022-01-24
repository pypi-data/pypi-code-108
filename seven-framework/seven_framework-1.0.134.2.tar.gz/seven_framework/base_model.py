# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-03-06 23:17:54
:LastEditTime: 2022-01-24 18:22:04
:LastEditors: ChenXiaolei
:Description: 数据库基础操作类
"""

from seven_framework.mysql import MySQLHelper
import datetime
import os
from seven_framework import *


class BaseModel:
    def __init__(self, model_class, sub_table):
        """
        :Description: 基础数据库操作类
        :param model_class: 实体对象类
        :param sub_table: 分表标识
        :last_editors: ChenXiaolei
        """
        # 实体对象类
        self.model_class = model_class
        # 实体对象
        self.model_obj = model_class()
        # 数据库表名
        self.table_name = str(self.model_obj) if not sub_table else str(
            self.model_obj).lower().replace("_tb", f"_{sub_table}_tb")
        # 主键字段名
        self.primary_key_field = self.model_obj.get_primary_key()

    def __convert_field_type(self, field_value):
        """
        :Description: 数据库字段类型兼容转换
        :param field_value: 字段值
        :return: 转换类型后的字段值
        :last_editors: ChenXiaolei
        """
        if isinstance(field_value, datetime.datetime):
            return field_value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(field_value, datetime.date):
            return field_value.strftime("%Y-%m-%d")
        elif isinstance(field_value, bytes):
            return field_value.decode()
        elif isinstance(field_value, decimal.Decimal):
            return str(decimal.Decimal(field_value).quantize(decimal.Decimal('0.00')))
        return field_value

    def __row_entity(self, data):
        """
        :Description: 单条数据转成对象
        :param data :数据字典
        :return: 模型实体
        :last_editors: ChenXiaolei
        """
        field_list = self.model_obj.get_field_list()
        if data is None or len(field_list) == 0:
            return None
        model_entity = self.model_class()
        for field_str in field_list:
            data[field_str] = self.__convert_field_type(data[field_str])
            setattr(model_entity, field_str, data[field_str])
        return model_entity

    def __row_entity_list(self, data_list):
        """
        :Description: 数据列表返回对象
        :param data_list: 数据字典数组
        :return: 模型实体列表
        :last_editors: ChenXiaolei
        """
        field_list = self.model_obj.get_field_list()
        if data_list is None or len(field_list) == 0:
            return None
        model_entity_list = []
        if len(data_list) > 0:
            for data in data_list:
                model_entity = self.model_class()
                for field_str in field_list:
                    if field_str in data:
                        data[field_str] = self.__convert_field_type(
                            data[field_str])
                        setattr(model_entity, field_str, data[field_str])
                model_entity_list.append(model_entity)
        return model_entity_list

    def get_list(self, where='', group_by='', order_by='', limit='', params=None):
        """
        :Description: 根据条件获取列表
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param params: 参数化查询参数
        :return: 模型实体列表
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        if limit:
            limit = " LIMIT "+str(limit)
        sql = f"SELECT * FROM {self.table_name}{where}{group_by}{order_by}{limit};"
        list_row = self.db.fetch_all_rows(sql, params)
        return self.__row_entity_list(list_row)

    def get_page_list(self,
                      field,
                      page_index,
                      page_size,
                      where='',
                      group_by='',
                      order_by='',
                      params=None):
        """
        :Description: 分页获取数据
        :param field: 查询字段 
        :param page_index: 分页页码 0为第一页
        :param page_size: 分页返回数据数量
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param params: 参数化查询参数
        :return: 模型实体列表
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY " + group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by

        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by} LIMIT {str(int(page_index) * int(page_size))},{str(page_size)};"
        list_row = self.db.fetch_all_rows(sql, params)

        sql = f"SELECT COUNT({self.primary_key_field}) AS count FROM {self.table_name}{where}{group_by}"

        if group_by:
            sql = f"SELECT COUNT(*) as count FROM ({sql}) temp_table;"

        row = self.db.fetch_one_row(sql, params)

        if row and 'count' in row and int(row['count']) > 0:
            row_count = int(row["count"])
        else:
            row_count = 0

        return self.__row_entity_list(list_row), row_count

    def get_entity(self, where='', group_by='', order_by='',  params=None):
        """
        :Description: 根据条件获取实体对象
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param params: 参数化查询参数
        :return: 模型实体
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        sql = f"SELECT * FROM {self.table_name}{where}{group_by}{order_by} LIMIT 1;"
        list_row = self.db.fetch_one_row(sql, params)
        return self.__row_entity(list_row)

    def get_entity_by_id(self, primary_key_id):
        """
        :Description: 根据主键值获取实体对象
        :param primary_key_id: 主键ID值 
        :return: 模型实体
        :last_editors: ChenXiaolei
        """
        sql = f"SELECT * FROM {self.table_name} WHERE {self.primary_key_field}=%s;"
        list_row = self.db.fetch_one_row(sql, [primary_key_id])
        return self.__row_entity(list_row)

    def get_total(self, where='', group_by='', field=None, params=None):
        """
        :Description: 根据条件获取数据数量
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param params: 参数化查询参数
        :param field: count(传参)
        :return: 查询符合条件的行的数量
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if not field:
            field = self.primary_key_field
        sql = f"SELECT COUNT({field}) AS count FROM {self.table_name}{where}{group_by}"

        if group_by:
            sql = f"SELECT COUNT(*) as count FROM ({sql}) temp_table;"

        list_row = self.db.fetch_one_row(sql, params)

        if list_row and 'count' in list_row:
            return list_row['count']
        return 0

    def del_entity(self, where, params=None):
        """
        :Description: 根据条件删除数据库中的数据
        :param where: 数据库查询条件语句
        :param params: 参数化查询参数
        :return: 
        :last_editors: ChenXiaolei
        """
        if where:
            where = " WHERE " + where
            sql = "DELETE FROM " + self.table_name + where

            if self.is_transaction():
                transaction_item = {}
                transaction_item["sql"] = sql
                transaction_item["params"] = params
                self.db_transaction.transaction_list.append(transaction_item)
                return True
            else:
                list_row = self.db.delete(sql, params)
                if list_row is not None and list_row > 0:
                    return True
                else:
                    return False

    def add_entity(self, model, ignore=False, return_increment_primary=True):
        """
        :Description: 数据入库
        :param model: 模型实体 
        :return: 非事务:如果主键为自增ID，返回自增ID
        :last_editors: ChenXiaolei
        """
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return 0
        insert_field_str = ""
        insert_value_str = ""
        param = []
        for field_str in field_list:
            param_value = str(getattr(model, field_str))
            if str(field_str).lower() == self.primary_key_field.lower() and param_value == "0":
                continue
            insert_field_str += str(field_str + ",")
            insert_value_str += "%s,"
            param.append(param_value)
        insert_field_str = insert_field_str.rstrip(',')
        insert_value_str = insert_value_str.rstrip(',')
        sql = f"INSERT{' IGNORE' if ignore else ''} INTO {self.table_name}({insert_field_str}) VALUE({insert_value_str});"
        if self.is_transaction():
            transaction_item = {}
            transaction_item["sql"] = sql
            transaction_item["params"] = tuple(param)
            self.db_transaction.transaction_list.append(transaction_item)
            return True
        else:
            list_row = self.db.insert(sql, tuple(
                param), return_increment_primary)
            return list_row

    def add_list(self, model_list, ignore=False, transaction=False):
        """
        :Description: 实体列表入库
        :param model_list: 实体列表
        :param ignore: 忽略已存在的记录
        :param transaction: 是否事务提交
        :return: 执行成功True 执行失败False
        :last_editors: ChenXiaolei
        """
        if not model_list or len(model_list) == 0:
            return False
        sql_list = []
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return False
        for model in model_list:
            insert_field_str = ""
            insert_value_str = ""
            param = []
            for field_str in field_list:
                param_value = str(getattr(model, field_str))
                if str(field_str).lower() == self.primary_key_field.lower() and param_value == "0":
                    continue
                insert_field_str += str(field_str + ",")
                insert_value_str += "%s,"
                param.append(param_value)
            insert_field_str = insert_field_str.rstrip(',')
            insert_value_str = insert_value_str.rstrip(',')
            sql = f"INSERT{' IGNORE' if ignore else ''} INTO {self.table_name}({insert_field_str}) VALUE({insert_value_str});"

            sql_item = {}
            sql_item["sql"] = sql
            sql_item["params"] = tuple(param)
            if self.is_transaction():
                self.db_transaction.transaction_list.append(sql_item)
            elif transaction:
                sql_list.append(sql_item)
            else:
                self.db.insert(sql, tuple(param))
        if transaction and not self.is_transaction():
            if not self.transaction_execute(sql_list):
                return False
        return True

    def add_values(self, model_list, ignore=False):
        """
        :description: 一次性数据写入(insert into... values(...),(...),(...);)
        :param model_list: 数据模型列表
        :param ignore: 忽略已存在的记录
        :return 成功True 失败False
        :last_editors: ChenXiaolei
        """
        if not model_list or len(model_list) == 0:
            return False
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return False

        insert_field_str = ""
        for field_str in field_list:
            if str(field_str).lower() == self.primary_key_field.lower():
                continue
            insert_field_str += str(field_str + ",")

        insert_field_str = insert_field_str.rstrip(',')

        sql = f"INSERT{' IGNORE' if ignore else ''} INTO {self.table_name}({insert_field_str}) VALUES "

        param = []
        for model in model_list:
            insert_value_str = ""

            for field_str in field_list:
                param_value = str(getattr(model, field_str))
                if str(field_str).lower() == self.primary_key_field.lower():
                    continue
                insert_value_str += "%s,"
                param.append(param_value)
            insert_value_str = insert_value_str.rstrip(',')
            sql += f"({insert_value_str}),"

        sql = sql.rstrip(',')+";"

        if self.is_transaction():
            sql_item = {}
            sql_item["sql"] = sql
            sql_item["params"] = tuple(param)
            self.db_transaction.transaction_list.append(sql_item)
        else:
            self.db.insert(sql, tuple(param), False)
        return True

    def add_update_entity(self, model, update_sql, params=None, return_increment_primary=True):
        """
        :Description: 数据入库,遇到主键冲突则更新指定字段
        :param model: 模型实体 
        :param update_sql: 如果主键冲突则执行的更新sql语句
        :param params: 参数化查询参数
        :param return_increment_primary: True=返回自增主键ID False=返回影响行数
        :return: 如果主键为自增ID，返回主键值
        :last_editors: ChenXiaolei
        """
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return 0
        insert_field_str = ""
        insert_value_str = ""
        param = []
        for field_str in field_list:
            param_value = str(getattr(model, field_str))
            if str(field_str).lower() == self.primary_key_field.lower() and param_value == "0":
                continue
            insert_field_str += str(field_str + ",")
            insert_value_str += "%s,"
            param.append(param_value)
        if params:
            param = param+params
        insert_field_str = insert_field_str.rstrip(',')
        insert_value_str = insert_value_str.rstrip(',')
        sql = f"INSERT INTO {self.table_name}({insert_field_str}) VALUE({insert_value_str}) ON DUPLICATE KEY UPDATE {update_sql};"
        if self.is_transaction():
            transaction_item = {}
            transaction_item["sql"] = sql
            transaction_item["params"] = tuple(param)
            self.db_transaction.transaction_list.append(transaction_item)
            return True
        else:
            list_row = self.db.insert(sql, tuple(
                param), return_increment_primary)
            return list_row

    def add_update_whole_entity(self, model, exclude_duplicate_key_field_list=None, return_increment_primary=True):
        """
        :Description: 数据入库,遇到主键冲突则更新指定字段
        :param model: 模型实体 
        :param exclude_duplicate_key_field_list: 触发唯一键时需排除更新的字段列表
        :param return_increment_primary: True=返回自增主键ID False=返回影响行数
        :return: 如果主键为自增ID，返回主键值
        :last_editors: ChenXiaolei
        """
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return 0
        insert_field_str = ""
        insert_value_str = ""
        update_sql = ""
        param = []
        update_param = []
        for field_str in field_list:
            param_value = str(getattr(model, field_str))
            if str(field_str).lower() == self.primary_key_field.lower() and param_value == "0":
                continue
            insert_field_str += str(field_str + ",")
            insert_value_str += "%s,"
            param.append(param_value)

            if exclude_duplicate_key_field_list and field_str not in exclude_duplicate_key_field_list:
                update_sql += f"{field}=%s,"
                update_param.append(param_value)

        insert_field_str = insert_field_str.rstrip(',')
        insert_value_str = insert_value_str.rstrip(',')
        update_sql = update_sql.rstrip(',')

        param.extend(update_param)

        sql = f"INSERT INTO {self.table_name}({insert_field_str}) VALUE({insert_value_str}) ON DUPLICATE KEY UPDATE {update_sql};"
        if self.is_transaction():
            transaction_item = {}
            transaction_item["sql"] = sql
            transaction_item["params"] = tuple(param)
            self.db_transaction.transaction_list.append(transaction_item)
            return True
        else:
            list_row = self.db.insert(sql, tuple(
                param), return_increment_primary)
            return list_row

    def update_entity(self, model, field_list=None, exclude_field_list=None):
        """
        :Description: 根据模型的主键ID，更新字段的值
        :param model: 模型实体
        :param field_list: 需要更新的字段列表
        :param exclude_field_list: 排除不需要更新的字段列表
        :return: 更新成功返回主键ID，否则返回空字符串
        :last_editors: ChenXiaolei
        """
        if not field_list:
            field_list = self.model_obj.get_field_list()
        elif type(field_list) == str:
            field_list = field_list.split(",")

        exclude_field = None

        if exclude_field_list and type(exclude_field_list) == list:
            exclude_field = exclude_field_list
        elif exclude_field_list and type(exclude_field_list) == str:
            exclude_field = exclude_field_list.split(",")

        if exclude_field:
            for exclude_field in exclude_field_list:
                if exclude_field in field_list:
                    field_list.remove(exclude_field)

        if len(field_list) == 0:
            return 0
        update_field_str = ""

        param = []
        mid = getattr(model, self.primary_key_field)
        for field_str in field_list:
            if self.primary_key_field and str(field_str).lower() == self.primary_key_field.lower():
                continue
            update_field_str += str(field_str + "=%s,")
            if str(field_str).lower() == "edit_on":
                now = datetime.datetime.now()
                param.append(str(now.strftime("%Y-%m-%d %H:%M:%S")))
            else:
                param.append(str(getattr(model, field_str)))
        param.append(mid)
        update_field_str = update_field_str.rstrip(',')
        if mid == 0:
            return 0
        sql = f"UPDATE {self.table_name} SET {update_field_str} WHERE {self.primary_key_field}=%s;"
        if self.is_transaction():
            transaction_item = {}
            transaction_item["sql"] = sql
            transaction_item["params"] = tuple(param)
            self.db_transaction.transaction_list.append(transaction_item)
            return True
        else:
            data = self.db.update(sql, tuple(param))
            if data is not None and data > 0:
                return mid
            else:
                return ""

    def update_list(self, model_list, field_list=None, exclude_field_list=None, transaction=False):
        """
        :Description: 根据模型的主键ID，更新字段的值
        :param model: 模型实体
        :return: 更新成功True  更新失败Flase
        :last_editors: ChenXiaolei
        """
        if not model_list or len(model_list) == 0:
            return False
        sql_list = []
        if not field_list:
            field_list = self.model_obj.get_field_list()
        elif type(field_list) == str:
            field_list = field_list.split(",")

        exclude_field = None

        if exclude_field_list and type(exclude_field_list) == list:
            exclude_field = exclude_field_list
        elif exclude_field_list and type(exclude_field_list) == str:
            exclude_field = exclude_field_list.split(",")

        if exclude_field:
            for exclude_field in exclude_field_list:
                if exclude_field in field_list:
                    field_list.remove(exclude_field)

        if len(field_list) == 0:
            return 0
        for model in model_list:
            update_field_str = ""

            param = []
            mid = getattr(model, self.primary_key_field)
            for field_str in field_list:
                if self.primary_key_field and str(field_str).lower() == self.primary_key_field.lower():
                    continue
                update_field_str += str(field_str + "=%s,")
                if str(field_str).lower() == "edit_on":
                    now = datetime.datetime.now()
                    param.append(str(now.strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    param.append(str(getattr(model, field_str)))
            param.append(mid)
            update_field_str = update_field_str.rstrip(',')
            if mid == 0:
                continue
            sql = f"UPDATE {self.table_name} SET {update_field_str} WHERE {self.primary_key_field}=%s;"
            if self.is_transaction():
                transaction_item = {}
                transaction_item["sql"] = sql
                transaction_item["params"] = tuple(param)
                self.db_transaction.transaction_list.append(transaction_item)
            elif transaction:
                transaction_item = {}
                transaction_item["sql"] = sql
                transaction_item["params"] = tuple(param)
                sql_list.append(transaction_item)
            else:
                self.db.update(sql, tuple(param))
        if transaction and not self.is_transaction():
            if not self.transaction_execute(sql_list):
                return False
        return True

    def update_table(self, update_sql, where, params=None):
        """
        :Description: 更新数据表
        :param update_sql: 更新set语句
        :param where: 数据库查询条件语句
        :param params: 参数化查询参数
        :return: 更新成功即为True 失败则为False
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        sql = f"UPDATE {self.table_name} SET {update_sql}{where};"
        if self.is_transaction():
            transaction_item = {}
            transaction_item["sql"] = sql
            transaction_item["params"] = params
            self.db_transaction.transaction_list.append(transaction_item)
            return True
        else:
            data = self.db.update(sql, params)
            if data is not None and data > 0:
                return True
            else:
                return False

    def get_dict(self, where='', group_by='', order_by='', limit='1', field="*", params=None):
        """
        :Description: 返回字典dict
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param field: 查询字段 
        :param params: 参数化查询参数
        :return: 返回匹配条件的第一行字典数据
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        if limit:
            limit = " LIMIT "+str(limit)
        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by}{limit};"
        one_row = self.db.fetch_one_row(sql, params)
        return one_row  # self.__row_entity(list_row)

    def get_dict_by_id(self, primary_key_id, field="*"):
        """
        :Description: 根据主键ID获取dict
        :param primary_key_id: 主键id值 
        :param field: 查询字段 
        :return: 返回匹配id的第一行字典数据
        :last_editors: ChenXiaolei
        """
        sql = f"SELECT {field} FROM {self.table_name} WHERE {self.primary_key_field}=%s;"
        one_row = self.db.fetch_one_row(sql, primary_key_id)
        return one_row

    def get_dict_list(self, where='', group_by='', order_by='', limit='', field="*", params=None):
        """
        :Description: 返回字典列表dict list
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param field: 查询字段 
        :param params: 参数化查询参数
        :return: 
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        if limit:
            limit = " LIMIT "+str(limit)
        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by}{limit};"
        list_row = self.db.fetch_all_rows(sql, params)

        if not list_row:
            list_row = []

        return list_row

    def get_dict_page_list(self,
                           field,
                           page_index,
                           page_size,
                           where='',
                           group_by='',
                           order_by='',
                           params=None):
        """
        :Description: 获取分页字典数据
        :param field: 查询字段 
        :param page_index: 分页页码 0为第一页
        :param page_size: 分页返回数据数量
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param params: 参数化查询参数
        :return: 数据字典数组
        :last_editors: ChenXiaolei
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY " + group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by

        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by} LIMIT {str(int(page_index) * int(page_size))},{str(page_size)}"
        list_row = self.db.fetch_all_rows(sql, params)

        if not list_row:
            list_row = []

        sql = f"SELECT COUNT({self.primary_key_field}) AS count FROM {self.table_name}{where}{group_by}"

        if group_by:
            sql = f"SELECT COUNT(*) as count FROM ({sql}) temp_table"
        row = self.db.fetch_one_row(sql, params)

        if row and 'count' in row and int(row['count']) > 0:
            row_count = int(row["count"])
        else:
            row_count = 0

        return list_row, row_count

    def transaction_execute(self, sql_list):
        """
        :Description: 执行事务,失败回滚
        :param sql_list:事务SQL字符串数组
        :return: 执行成功True 执行失败False
        :last_editors: ChenXiaolei
        """
        if not sql_list or len(sql_list) == 0:
            return False
        return self.db.transaction_execute(sql_list)

    def is_transaction(self):
        """
        :Description: 是否开启事务
        :last_editors: ChenXiaolei
        """
        if hasattr(self, "db_transaction") and self.db_transaction and self.db_transaction.is_transaction == True:
            return True
        return False

    def build_add_sql(self, model_list, ignore=False):
        """
        :Description: 构造insert sql语句
        :param model_list: 实体列表
        :param ignore: 忽略已存在的记录
        :return: sql语句字符串
        :last_editors: ChenXiaolei
        """
        if not model_list or len(model_list) == 0:
            return ""
        build_sql = ""
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return ""
        for model in model_list:
            insert_field_str = ""
            insert_value_str = ""
            for field_str in field_list:
                param_value = str(getattr(model, field_str))
                if str(field_str).lower() == self.primary_key_field.lower() and param_value == "0":
                    continue
                insert_field_str += str(field_str + ",")
                insert_value_str += f"'{param_value}',"
            insert_field_str = insert_field_str.rstrip(',')
            insert_value_str = insert_value_str.rstrip(',')
            sql = f"INSERT{' IGNORE' if ignore else ''} INTO {self.table_name}({insert_field_str}) VALUE({insert_value_str});"
            build_sql = build_sql+sql
        return build_sql

    def build_update_sql(self, model_list, field_list=None):
        """
        :Description: 构造update sql语句
        :param model_list: 实体列表
        :param field_list: 需要更新的字段
        :return: sql语句字符串
        :last_editors: ChenXiaolei
        """
        if not model_list or len(model_list) == 0:
            return ""
        build_sql = ""
        if not field_list:
            field_list = self.model_obj.get_field_list()
        elif type(field_list) == str:
            field_list = field_list.split(',')
        if len(field_list) == 0:
            return 0
        for model in model_list:
            update_field_str = ""
            for field_str in field_list:
                if self.primary_key_field and str(field_str).lower() == self.primary_key_field.lower():
                    continue
                if str(field_str).lower() == "edit_on":
                    update_field_str += f"{str(field_str)}='{TimeHelper.get_now_format_time()}',"
                else:
                    update_field_str += f"{str(field_str)}='{str(getattr(model, field_str))}',"

            update_field_str = update_field_str.rstrip(',')
            build_sql = build_sql + \
                f"UPDATE {self.table_name} SET {update_field_str} WHERE {self.primary_key_field}='{getattr(model,self.primary_key_field)}';"
        return build_sql

    def build_data_sql(self, model_list):
        """
        :Description: 构造replace sql语句
        :param model_list: 实体列表
        :return: sql语句字符串
        :last_editors: ChenXiaolei
        """
        if not model_list or len(model_list) == 0:
            return ""
        build_sql = ""
        field_list = self.model_obj.get_field_list()
        if len(field_list) == 0:
            return ""
        for model in model_list:
            insert_field_str = ""
            insert_value_str = ""
            for field_str in field_list:
                insert_field_str += str(field_str + ",")
                insert_value_str += f"'{str(getattr(model, field_str))}',"
            insert_field_str = insert_field_str.rstrip(',')
            insert_value_str = insert_value_str.rstrip(',')
            sql = f"REPLACE INTO {self.table_name}({insert_field_str}) VALUE({insert_value_str});"
            build_sql = build_sql+sql
        return build_sql
