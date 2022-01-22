#!/usr/bin/env python3
# coding: utf-8

import sqlalchemy
import sqlalchemy.dialects.sqlite
from sqlalchemy.sql.selectable import Select, Selectable


def _as_column(c):
    if not isinstance(c, str):
        return c
    return sqlalchemy.column(c)


def simple_select(table, columns) -> Select:
    if isinstance(table, str):
        table = sqlalchemy.text(table)
    columns = [_as_column(c) for c in columns]
    return sqlalchemy.select(columns).select_from(table)


def stringify(stmt: Selectable, dialect=None) -> str:
    if dialect is None:
        dialect = sqlalchemy.dialects.sqlite.dialect()
    cpl = stmt.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
    return str(cpl)
