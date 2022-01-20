import abc
import typing

from sqlalchemy import Boolean, Column, Table
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.elements import BooleanClauseList


class Filter:
    _mark: str = ''

    def where(self, entity: typing.Union[type, Table]):
        pass

    def __bool__(self):
        return False

    @property
    def mark(self):
        return self._mark

    def add_mark(self, mark: str):
        self._mark = mark
        return self


class Comparison(abc.ABC):
    @abc.abstractmethod
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        """Receives column or function and returns a sqlalchemy comparison"""
