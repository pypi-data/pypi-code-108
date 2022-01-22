#!/usr/bin/env python3
# coding: utf-8

import itertools
import logging
import os
import time
import typing
from typing import Union

import sqlalchemy
import sqlalchemy.exc
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy import text

_logger = logging.getLogger(__name__)


# noinspection SqlNoDataSourceInspection
class SQLInterface:
    _loglevel = logging.INFO

    def __init__(self, engine: Engine, metadata: MetaData):
        self.engine = engine
        self.metadata = metadata
        self._pid = os.getpid()

    @classmethod
    def from_config(cls, options: dict, metadata: MetaData = None):
        engine = sqlalchemy.create_engine(**options)
        return cls(engine, metadata or MetaData())

    def execute(self, statement):
        if _logger.isEnabledFor(self._loglevel):
            _logger.log(self._loglevel, str(statement))
        with self.engine.begin() as conn:
            return conn.execute(statement)

    def __call__(self, statement):
        return self.execute(statement)

    def execute_script(self, path: str):
        try:
            conn = self.engine.raw_connection()
            _logger.debug('execute sql script: %s', path)
            return conn.execute(open(path).read(), multi=True)
        finally:
            conn.close()

    def just_after_fork(self):
        # http://docs.sqlalchemy.org/en/latest/core/pooling.html
        # section "Using Connection Pools with Multiprocessing"
        if self._pid != os.getpid():
            self.engine.dispose()
            self._pid = os.getpid()

    def create_tables(self, fullnames: list = None, ignore='*_view'):
        if _logger.isEnabledFor(logging.INFO):
            names = self.metadata.tables if fullnames is None else fullnames
            _logger.info('creating tables: %s', ' '.join(names))
        if fullnames is None:
            return self.metadata.create_all(self.engine)
        tables = [self.metadata.tables[name] for name in fullnames]
        if ignore:
            tables = [t for t in tables if not fnmatchcase(t.name, ignore)]
        return self.metadata.create_all(self.engine, tables=tables)

    def get_sibling_engine(self, database: str, **kwargs) -> Engine:
        url = self.engine.url.set(database=database)
        return sqlalchemy.create_engine(url, **kwargs)

    def get_sibling(self, database: str, **kwargs) -> 'SQLInterface':
        metadata = kwargs.get('metadata') or sqlalchemy.MetaData()
        engine = self.get_sibling_engine(database, **kwargs)
        return SQLInterface(engine, metadata)


class PostgreSQLInterface(SQLInterface):
    _preset_schemas = {'public'}

    def get_schemas(self) -> set:
        schemas = self._preset_schemas.copy()
        for tbl in self.metadata.tables.values():
            if tbl.schema is None:
                continue
            schemas.add(tbl.schema)
        return schemas

    def create_schemas(self, schemas: list = None):
        if schemas is None:
            schemas = self.get_schemas()
        for schema in schemas:
            _logger.info('creating schema: %s', schema)
            stmt = text(f'CREATE SCHEMA IF NOT EXISTS {schema};')
            self.execute(stmt)

    def refresh_materialized_views(self, mviews: list, concurrently=True):
        # https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html
        for v in mviews:
            if concurrently:
                self.execute(f'REFRESH MATERIALIZED VIEW CONCURRENTLY {v};')
            else:
                self.execute(f'REFRESH MATERIALIZED VIEW {v};')
            _logger.info('mview refreshed: %s', v)
        return mviews


# noinspection SqlNoDataSourceInspection
class PostgreSQLAdminInterface(PostgreSQLInterface):
    def wait_until_server_ready(
            self, timeout: int = 30,
            interval: Union[int, float, typing.Iterable] = 3):
        """
        Args:
            timeout: in second
            interval: a number or an iterable of numbers (e.g. [1, 2, 4, ...])
        Returns:
            None
        """
        start = time.time()
        if isinstance(interval, (int, float)):
            interval = itertools.repeat(interval)
        else:
            interval = itertools.cycle(interval)
        for sec in interval:
            try:
                # language=SQL
                self.execute('SELECT 1;').scalar()
                _logger.info('database server is ready now!')
                return
            except sqlalchemy.exc.OperationalError as exc:
                _logger.info(
                    'database server is not ready: %s -- %s',
                    self.engine.url, exc.args[0],
                )
            remaining = timeout + start - time.time()
            if remaining < 0:
                break
            time.sleep(min(remaining, sec))
        _logger.info('failed to connect to %s', self.engine.url)

    def exists(self, database: str):
        # https://www.postgresql.org/docs/current/catalog-pg-database.html
        # alternative: from sqlalchemy_utils.functions import database_exists
        sql = f"SELECT 1 FROM pg_database WHERE datname='{database}';"
        try:
            return bool(self.execute(sql).scalar())
        except sqlalchemy.exc.OperationalError:
            return False

    def create_database(self, name: str):
        if self.exists(name):
            _logger.info('database exists already, creation skipped')
            return
        with self.engine.connect():
            # language=SQL
            sql = f'CREATE DATABASE {name};'
            self.execute(sql)
