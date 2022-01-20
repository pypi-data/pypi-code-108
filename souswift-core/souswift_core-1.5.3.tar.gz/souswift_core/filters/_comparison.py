import typing
from abc import ABC, abstractmethod

from sqlalchemy import Boolean, Column, func
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.expression import ColumnElement

from souswift_core.filters.base import Comparison, Filter


class Equal(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr == target


class NotEqual(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr != target


class Greater(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr > target


class GreaterEqual(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr >= target


class Lesser(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr < target


class LesserEqual(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr <= target


class Like(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.like(f'%{target}%')


class InsensitiveLike(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.ilike(f'%{target}%')


class Contains(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.in_(target)


class Excludes(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.not_in(target)


class Null(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], isnull: bool
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.is_(None) if isnull else attr.is_not(None)


class JSONContains(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return func.json_contains(attr, f'"{target}"')  # type: ignore


class EmptyJson(Comparison):
    def compare(
        self, attr: typing.Union[Column, typing.Any], target: typing.Any
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return func.json_length(attr) == 0


class RelatedComp(ABC):
    def __init__(self, where: Filter):
        self._where = where

    def __bool__(self):
        return self._where.__bool__()

    @abstractmethod
    def compare(
        self, attr: type, target: typing.Union[Column, typing.Any]
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        ...


class RelatedWhere(RelatedComp):
    def compare(
        self, attr: type, target: typing.Union[Column, typing.Any]
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return self._where.where(attr)


class RelatedHas(RelatedComp):
    def compare(
        self, attr: type, target: typing.Union[Column, typing.Any]
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.has(self._where.where(attr))


class RelatedAny(RelatedComp):
    def compare(
        self, attr: type, target: typing.Union[Column, typing.Any]
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return attr.any(self._where.where(attr))


class RelatedEmpty(RelatedComp):
    def compare(
        self, attr: type, target: typing.Union[Column, typing.Any]
    ) -> typing.Union[BooleanClauseList, 'ColumnElement[Boolean]']:
        return ~target.any()
