import abc
from typing import Any

from utils.enums import LikeEnum, QueryModeEnum


class Limit:
    __slots__ = ['start', 'count']

    start: int
    count: int

    def __init__(self, start: int, count: int = None):
        self.start = start
        self.count = count

    def __str__(self):
        if self.count is None:
            return f' limit {self.start}'
        return f' limit {self.start}, {self.count}'


class Like:
    __slots__ = ['sql', 'value', 'column']

    sql: str
    column: str
    value: str

    def __init__(self, column: str, value, like_type: LikeEnum):
        self.column = column
        self.value = value
        self.sql = f' {column} like'
        if like_type == LikeEnum.L_Like:
            self.sql += f' concat(\'%%\',%({column})s)'
        elif like_type == LikeEnum.R_Like:
            self.sql += f' concat(%({column})s,\'%%\')'
        elif like_type == LikeEnum.ALL_Like:
            self.sql += f' concat(\'%%\',%({column})s,\'%%\')'

    def __str__(self):
        return self.sql


def extra(column: list, data_property: str, method):
    """
    :param column: table A[column[0]] mapping table B[column[1]]
    :param data_property: table A property name
    :param method: query method
    """

    def e(data_entity):
        if isinstance(data_entity, list):
            for entity in data_entity:
                entity.__setattr__(data_property,
                                   method(**{column[1]: data_entity.__getattribute__(column[0])}))
            return data_entity
        data_entity.__setattr__(data_property,
                                method(**{column[1]: data_entity.__getattribute__(column[0])}))
        return data_entity

    return e
