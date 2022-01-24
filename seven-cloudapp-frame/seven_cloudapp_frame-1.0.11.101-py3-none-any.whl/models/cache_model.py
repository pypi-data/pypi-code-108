# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-03-06 23:17:54
@LastEditTime: 2022-01-21 21:24:03
@LastEditors: HuangJianYi
:Description: 数据库基础操作类
"""
import json
from copy import deepcopy
from seven_framework.base_model import *
from seven_framework import *
from seven_framework.redis import *


class CacheModel(BaseModel):

    def __init__(self, model_class, sub_table):
        """
        :Description: 数据缓存业务模型
        :param model_class: 实体对象类
        :param sub_table: 分表标识
        :last_editors: HuangJianYi
        """
        super(CacheModel,self).__init__(model_class, sub_table)

    def __get_dependency_key(self, dependency_key=''):
        """
        :Description: 获取依赖建
        :param dependencyKey: 依赖键
        :return: 依赖建
        :last_editors: HuangJianYi
        """
        if not dependency_key:
            dependency_key = "dependency_" + self.table_name.lower()
        return dependency_key

    def __get_cache_key(self, field, where='', group_by='', order_by='', limit='', params=None):
        """
        :Description: 获取缓存key
        :param field: 查询字段
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param params: 参数化查询参数
        :return: 缓存key
        :last_editors: HuangJianYi
        """
        params_str = ""
        if params:
            if isinstance(params,list):
                for param in params:
                    params_str += "_" + str(param)
            else:
                params_str += "_" + str(params)
        cache_key = str(field + "_" + where + "_" + group_by + "_" + order_by + "_" + limit + params_str).replace(" ", "").lower()
        return CryptoHelper.md5_encrypt(cache_key)

    def __get_dependency_cache_key(self, dependency_key, cache_key):
        """
        :Description: 获取依赖缓存key
        :param dependency_key: 依赖键
        :param cache_key: 缓存key
        :return: 依赖缓存key
        :last_editors: HuangJianYi
        """
        return CryptoHelper.md5_encrypt(dependency_key+cache_key)

    def __get_dependency_cache(self, dependency_key, cache_key):
        """
        :Description: 获取依赖缓存值
        :param dependency_key: 依赖键
        :param cache_key: 缓存key
        :return: 依赖缓存值
        :last_editors: HuangJianYi
        """
        dependency_cache_key = self.__get_dependency_cache_key(dependency_key,cache_key)
        redis_init = self.__redis_init()
        dependency_date_value = redis_init.get(dependency_key)
        if not dependency_date_value:
            redis_init.delete(dependency_cache_key)
            return None
        dependency_date = TimeHelper.format_time_to_datetime(dependency_date_value)
        cache_savetime_key = dependency_cache_key + "_savetime"
        cache_savetime_value = redis_init.get(cache_savetime_key)
        if not cache_savetime_value:
            redis_init.delete(cache_savetime_key)
            redis_init.delete(dependency_cache_key)
            return None
        cache_savetime_date = TimeHelper.format_time_to_datetime(cache_savetime_value)
        if cache_savetime_date < dependency_date:
            redis_init.delete(cache_savetime_key)
            redis_init.delete(dependency_cache_key)
            return None
        cache_data = redis_init.get(dependency_cache_key)
        if not cache_data:
            return None
        elif cache_data == 'null':
            return cache_data
        elif cache_data == '0':
            return cache_data
        else:
            cache_data = json.loads(cache_data)
            return cache_data

    def __set_dependency_cache(self, dependency_key, cache_key,value, cache_expire):
        """
        :Description: 获取依赖缓存值
        :param dependency_key: 依赖键
        :param cache_key: 缓存key
        :param cache_expire: 缓存时间（单位秒）
        :return: 
        :last_editors: HuangJianYi
        """
        if not value:
            return
        redis_init = self.__redis_init()
        dependency_date_value = redis_init.get(dependency_key)
        if not dependency_date_value:
            redis_init.set(dependency_key,str(TimeHelper.get_now_format_time()),ex=config.get_value("dependency_cache_expire",60*60))
        dependency_cache_key = self.__get_dependency_cache_key(dependency_key,cache_key)
        redis_init.set(dependency_cache_key + "_savetime",str(TimeHelper.get_now_format_time()),ex=cache_expire)
        return redis_init.set(dependency_cache_key,JsonHelper.json_dumps(value),ex=cache_expire)

    def __redis_init(self, db=None, decode_responses=True):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJianYi
        """
        host = config.get_value("redis")["host"]
        port = config.get_value("redis")["port"]
        if not db:
            db = config.get_value("redis")["db"]
        password = config.get_value("redis")["password"]
        redis_cli = RedisHelper.redis_init(host, port, db, password, decode_responses=decode_responses)
        return redis_cli

    def delete_dependency_key(self, dependency_key=''):
        """
        :Description: 删除依赖键
        :param dependency_key: 依赖键,为空则删除默认依赖建
        :return: 
        :last_editors: HuangJianYi
        """
        redis_init = self.__redis_init()
        return redis_init.delete(self.__get_dependency_key(dependency_key))

    def get_cache_list(self, where='', group_by='', order_by='', limit='', field="*", params=None,dependency_key='', cache_expire=600):
        """
        :Description: 根据条件获取列表
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param field: 查询字段 
        :param params: 参数化查询参数
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 模型实体列表
        :last_editors: HuangJianYi
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

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "entitylist_" + self.table_name + "_" + self.__get_cache_key('*',where,group_by,order_by,limit,params)
        list_row = self.__get_dependency_cache(dependency_key,cache_key)
        if list_row and config.get_value("is_redis_cache",True) == True:
            if list_row == 'null':
                return None
            return self._BaseModel__row_entity_list(list_row)
        else:
            list_row = self.db.fetch_all_rows(sql, params)
            cache_value = deepcopy(list_row)
            if not cache_value:
                cache_value = None
            self.__set_dependency_cache(dependency_key,cache_key,cache_value,cache_expire)
            return self._BaseModel__row_entity_list(list_row)

    def get_cache_page_list(self, field="*", page_index=0, page_size=20, where='', group_by='', order_by='', params=None, dependency_key='', cache_expire=600):
        """
        :Description: 分页获取数据
        :param field: 查询字段 
        :param page_index: 分页页码 0为第一页
        :param page_size: 分页返回数据数量
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param params: 参数化查询参数
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 模型实体列表
        :last_editors: HuangJianYi
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY " + group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        limit = f"{str(int(page_index) * int(page_size))},{str(page_size)}"

        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by} LIMIT {limit};"
        count_sql = f"SELECT COUNT({self.primary_key_field}) AS count FROM {self.table_name}{where}{group_by};"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "entitypagelist_" + self.table_name + "_" + self.__get_cache_key(field,where,group_by,order_by,limit,params)
        page_list = self.__get_dependency_cache(dependency_key,cache_key)
        if page_list and config.get_value("is_redis_cache",True) == True:
            return self._BaseModel__row_entity_list(page_list["data"]),page_list["row_count"]
        else:
            list_row = self.db.fetch_all_rows(sql, params)
            row = self.db.fetch_one_row(count_sql, params)
            if row and 'count' in row and int(row['count']) > 0:
                row_count = int(row["count"])
            else:
                row_count = 0
            page_list = {}
            page_list["data"] = list_row
            page_list["row_count"] = row_count
            self.__set_dependency_cache(dependency_key,cache_key,page_list,cache_expire)
            return self._BaseModel__row_entity_list(page_list["data"]), row_count

    def get_cache_entity(self, where='', group_by='', order_by='',  params=None, dependency_key='', cache_expire=600):
        """
        :Description: 根据条件获取实体对象
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param params: 参数化查询参数
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 模型实体
        :last_editors: HuangJianYi
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        sql = f"SELECT * FROM {self.table_name}{where}{group_by}{order_by} LIMIT 1;"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "entity_" + self.table_name + "_" + self.__get_cache_key('*',where,group_by,order_by,'1',params)
        one_row = self.__get_dependency_cache(dependency_key,cache_key)
        if one_row and config.get_value("is_redis_cache",True) == True:
            if one_row == 'null':
                return None
            return self._BaseModel__row_entity(one_row)
        else:
            one_row = self.db.fetch_one_row(sql, params)
            self.__set_dependency_cache(dependency_key,cache_key,one_row,cache_expire)
            return self._BaseModel__row_entity(one_row)

    def get_cache_entity_by_id(self, primary_key_id, dependency_key='', cache_expire=600):
        """
        :Description: 根据主键值获取实体对象
        :param primary_key_id: 主键ID值
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 模型实体
        :last_editors: HuangJianYi
        """
        where = f"{self.primary_key_field}=%s"
        params = [primary_key_id]
        sql = f"SELECT * FROM {self.table_name} WHERE {where} LIMIT 1;"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "entityone_" + self.table_name + "_" + self.__get_cache_key('*',where,'','','',params)
        one_row = self.__get_dependency_cache(dependency_key,cache_key)
        if one_row and config.get_value("is_redis_cache",True) == True:
            if one_row == 'null':
                return None
            return self._BaseModel__row_entity(one_row)
        else:
            one_row = self.db.fetch_one_row(sql,params)
            self.__set_dependency_cache(dependency_key,cache_key,one_row,cache_expire)
            return self._BaseModel__row_entity(one_row)

    def get_cache_total(self, where='', group_by='', field=None, params=None,dependency_key='', cache_expire=600):
        """
        :Description: 根据条件获取数据数量
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param params: 参数化查询参数
        :param field: count(传参)
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 查询符合条件的行的数量
        :last_editors: HuangJianYi
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if not field:
            field = self.primary_key_field
        sql = f"SELECT COUNT({field}) AS count FROM {self.table_name}{where}{group_by};"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "total_" + self.table_name + "_" + self.__get_cache_key(field,where,group_by,'','',params)
        total = self.__get_dependency_cache(dependency_key,cache_key)
        if total and config.get_value("is_redis_cache",True) == True:
            if total == '0':
                return 0
            else:
                return total
        else:
            list_row = self.db.fetch_one_row(sql, params)
            if list_row and 'count' in list_row:
                self.__set_dependency_cache(dependency_key,cache_key,list_row['count'],cache_expire)
                return list_row['count']
            return 0

    def get_cache_dict(self, where='', group_by='', order_by='', limit='1', field="*", params=None, dependency_key='', cache_expire=600):
        """
        :Description: 返回字典dict
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param field: 查询字段 
        :param params: 参数化查询参数
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 返回匹配条件的第一行字典数据
        :last_editors: HuangJianYi
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY "+group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        if limit:
            limit = " LIMIT "+str(limit)
        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by}{limit}"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "dict_" + self.table_name + "_" + self.__get_cache_key(field,where,group_by,order_by,limit,params)
        one_row = self.__get_dependency_cache(dependency_key,cache_key)

        if one_row and config.get_value("is_redis_cache",True) == True:
            if one_row == 'null':
                return None
            return one_row
        else:
            one_row = self.db.fetch_one_row(sql, params)
            self.__set_dependency_cache(dependency_key,cache_key,one_row,cache_expire)
            if one_row:
                for field in one_row:
                    one_row[field] = self._BaseModel__convert_field_type(one_row[field])
            return one_row

    def get_cache_dict_by_id(self, primary_key_id, dependency_key='', cache_expire=600, field="*"):
        """
        :Description: 根据主键ID获取dict
        :param primary_key_id: 主键ID值
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :param field: 查询字段 
        :return: 返回匹配id的第一行字典数据
        :last_editors: HuangJianYi
        """
        where = f"{self.primary_key_field}=%s"
        params = [primary_key_id]
        sql = f"SELECT {field} FROM {self.table_name} WHERE {where} LIMIT 1;"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "dictone_" + self.table_name + "_" + self.__get_cache_key(field,where,'','','',params)
        one_row = self.__get_dependency_cache(dependency_key,cache_key)
        if one_row and config.get_value("is_redis_cache",True) == True:
            if one_row == 'null':
                return None
            return one_row
        else:
            one_row = self.db.fetch_one_row(sql,params)
            self.__set_dependency_cache(dependency_key,cache_key,one_row,cache_expire)
            if one_row:
                for field in one_row:
                    one_row[field] = self._BaseModel__convert_field_type(one_row[field])
            return one_row

    def get_cache_dict_list(self, where='', group_by='', order_by='', limit='', field="*", params=None, dependency_key='',cache_expire=600):
        """
        :Description: 返回字典列表dict list
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param limit:  LIMIT 语句
        :param field: 查询字段 
        :param params: 参数化查询参数
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 
        :last_editors: HuangJianYi
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

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "dictlist_" + self.table_name + "_" + self.__get_cache_key(field,where,group_by,order_by,limit,params)
        list = self.__get_dependency_cache(dependency_key,cache_key)
        if list and config.get_value("is_redis_cache",True) == True:
            return list
        else:
            list = self.db.fetch_all_rows(sql, params)
            self.__set_dependency_cache(dependency_key,cache_key,list,cache_expire)
            if list and len(list) > 0:
                for one_row in list:
                    for field in one_row:
                        one_row[field] = self._BaseModel__convert_field_type(one_row[field])
            return list

    def get_cache_dict_page_list(self, field="*", page_index=0 ,page_size=20, where='', group_by='' ,order_by='' ,params=None, dependency_key='', cache_expire=600):
        """
        :Description: 获取分页字典数据
        :param field: 查询字段 
        :param page_index: 分页页码 0为第一页
        :param page_size: 分页返回数据数量
        :param where: 数据库查询条件语句
        :param group_by: GROUP BY 语句
        :param order_by:  ORDER BY 语句
        :param params: 参数化查询参数
        :param dependencyKey: 依赖键
        :param cache_expire: 缓存时间（单位秒）
        :return: 数据字典数组
        :last_editors: HuangJianYi
        """
        if where and where.strip() != '':
            where = " WHERE " + where
        if group_by and group_by.strip() != '':
            group_by = " GROUP BY " + group_by
        if order_by and order_by.strip() != '':
            order_by = " ORDER BY " + order_by
        limit = f"{str(int(page_index) * int(page_size))},{str(page_size)}"
        sql = f"SELECT {field} FROM {self.table_name}{where}{group_by}{order_by} LIMIT {limit}"
        count_sql = f"SELECT COUNT({self.primary_key_field}) AS count FROM {self.table_name}{where}{group_by};"

        dependency_key = self.__get_dependency_key(str(dependency_key))
        cache_key = "dictpagelist_" + self.table_name + "_" + self.__get_cache_key(field,where,group_by,order_by,limit,params)
        page_list = self.__get_dependency_cache(dependency_key,cache_key)
        if page_list and config.get_value("is_redis_cache",True) == True:
            return page_list["data"],page_list["row_count"]
        else:
            list_row = self.db.fetch_all_rows(sql, params)
            row = self.db.fetch_one_row(count_sql, params)
            if row and 'count' in row and int(row['count']) > 0:
                row_count = int(row["count"])
            else:
                row_count = 0
            page_list = {}
            page_list["data"] = list_row
            page_list["row_count"] = row_count
            self.__set_dependency_cache(dependency_key,cache_key,page_list,cache_expire)
            if list_row and len(list_row) > 0:
                for one_row in list_row:
                    for field in one_row:
                        one_row[field] = self._BaseModel__convert_field_type(one_row[field])
            return list_row, row_count
