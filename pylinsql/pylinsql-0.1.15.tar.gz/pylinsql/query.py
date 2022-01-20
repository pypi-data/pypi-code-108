"""
Construct a SQL query from a Python expression.
"""

from __future__ import annotations

import functools
import inspect
import os.path
import sys
from dataclasses import dataclass
from types import CodeType
from typing import Generator, List, Type

from .base import DataClass, T
from .builder import Context, QueryBuilder, QueryBuilderArgs
from .core import EntityProxy, Query
from .decompiler import CodeExpression, CodeExpressionAnalyzer


def get_entity_types(sql_generator_expr: Generator) -> List[Type]:
    if not inspect.isgenerator(sql_generator_expr):
        raise TypeError(
            f"expected a SQL generator expression but got: {type(sql_generator_expr)}"
        )

    entity = sql_generator_expr.gi_frame.f_locals[".0"]
    if not isinstance(entity, EntityProxy):
        raise TypeError("invalid SQL generator expression")

    return entity.types


@functools.lru_cache
def _analyze_expression(code_object: CodeType) -> CodeExpression:
    code_analyzer = CodeExpressionAnalyzer(code_object)
    try:
        return code_analyzer.get_expression()
    except Exception as e:
        path = code_object.co_filename
        lineno = code_object.co_firstlineno
        raise RuntimeError(
            f'error parsing expression in file "{path}", line {lineno}'
        ) from e


@dataclass
class CacheInfo:
    hits: int
    misses: int


def cache_info() -> CacheInfo:
    info = _analyze_expression.cache_info()
    return CacheInfo(info.hits, info.misses)


def _query_builder_args(sql_generator_expr: Generator) -> QueryBuilderArgs:
    if not inspect.isgenerator(sql_generator_expr):
        raise TypeError(
            f"expected a SQL generator expression but got: {type(sql_generator_expr)}"
        )

    # obtain AST representation of generator expression
    code_expression = _analyze_expression(sql_generator_expr.gi_frame.f_code)

    # get reference to caller's frame
    package_root = os.path.dirname(__file__)
    caller = frame = sys._getframe(2)
    while frame:
        if not frame.f_code.co_filename.startswith(package_root):
            caller = frame
            break
        frame = frame.f_back

    # build query context
    context = Context(code_expression.local_vars, caller.f_locals, caller.f_globals)
    source_arg = sql_generator_expr.gi_frame.f_locals[".0"]

    # build SQL query
    return QueryBuilderArgs(
        source_arg,
        context,
        code_expression.conditional_expr,
        code_expression.yield_expr,
    )


def select(sql_generator_expr: Generator[T, None, None]) -> Query[T]:
    "Builds a query expression corresponding to a SELECT SQL statement."

    qba = _query_builder_args(sql_generator_expr)
    builder = QueryBuilder()
    return builder.select(qba)


def insert_or_select(
    insert_obj: DataClass[T], sql_generator_expr: Generator[T, None, None]
) -> Query[T]:
    "Builds a query expression corresponding to a combined SELECT or INSERT SQL statement."

    qba = _query_builder_args(sql_generator_expr)
    builder = QueryBuilder()
    return builder.insert_or_select(qba, insert_obj)
