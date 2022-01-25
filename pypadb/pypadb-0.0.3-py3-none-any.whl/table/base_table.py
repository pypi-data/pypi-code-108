from typing import Any, Union

from utils.conditions import Limit, Like
from utils.enums import QueryModeEnum
from utils.query_util import query, execute


def parse_sql(sql: str, conditions: dict, limit: Limit = None) -> str:
    if conditions:
        sql += ' where'
        for key in conditions:
            sql += f' {key}=%({key})s and'
    sql = sql.rstrip(' and')
    return sql + str(limit) if limit else sql


class BaseTable:
    __slots__ = ['name', 'data_type', 'base_select_sql']

    name: str
    data_type: Any
    base_select_sql: str

    def __init__(self, name: str, data_type):
        self.name = name
        self.data_type = data_type
        self.base_select_sql = f'select * from {name}'

    def select_one(self, extra=None, **kwargs):
        res = query(parse_sql(self.base_select_sql, kwargs), kwargs, self.data_type, QueryModeEnum.One)
        return extra(res) if extra else res

    def select_many(self, limit: Limit = None, extra=None, **kwargs) -> list:
        res = query(parse_sql(self.base_select_sql, kwargs, limit), kwargs, self.data_type, QueryModeEnum.Many)
        return extra(res) if extra else res

    def select_like(self,
                    likes: Union[list[Like], Like] = {},
                    limit: Limit = None,
                    extra=None) -> list:
        sql: str = self.base_select_sql
        data_dict: dict = {}
        if likes:
            sql += ' where'
            if isinstance(likes, list):
                for like in likes:
                    sql += f'{like} and'
                    data_dict[like.column] = like.value
                sql = sql.rstrip(' and')
            else:
                sql += str(likes)
                data_dict[likes.column] = likes.value
        res = query(sql + str(limit) if limit else sql, data_dict, self.data_type, QueryModeEnum.Many)
        return extra(res) if extra else res

    def update(self, entity, **kwargs):
        if not kwargs:
            return
        sql = f'update {self.name}'
        data_dict = entity.dict()
        if entity:
            sql += ' set'
            for key in data_dict:
                if data_dict[key] or data_dict[key] == 0:
                    sql += f' {key}=%({key})s,'
            sql = sql.rstrip(',')
        sql = parse_sql(sql, kwargs)
        return execute(sql, {**data_dict, **kwargs})

    def delete(self, **kwargs):
        if not kwargs:
            return
        sql = f'delete from {self.name}'
        sql = parse_sql(sql, kwargs)
        return execute(sql, kwargs)

    def insert(self, data):
        sql = f'insert into {self.name}('
        tmp = '('
        data_dict: dict = data.dict()
        for key in data_dict:
            if data_dict[key] or data_dict[key] == 0:
                sql += f'{key}, '
                tmp += f'%({key})s, '
        tmp = tmp.rstrip(', ') + ')'
        sql = sql.rstrip(', ') + ') value' + tmp
        return execute(sql, data_dict)

    def insert_batch(self, data: list):
        sql = f'insert into {self.name}('
        data_dict: dict = data[0].dict()
        for key in data_dict:
            if data_dict[key] or data_dict[key] == 0:
                sql += f' {key}, '
        sql = sql.rstrip(', ') + ') values '
        data_list_tmp: list[dict] = [i.dict() for i in data]
        data_dict = {}
        for i, v in enumerate(data_list_tmp):
            sql += '('
            for k in v:
                data_dict[f'{k}{i}'] = v[k]
                sql += f'%({k}{i})s, '
            sql = sql.rstrip(', ') + '), '
        sql = sql.rstrip(', ')
        print(sql, data_dict)
        return execute(sql, data_dict)
