import logging
import time
import typing
from contextlib import contextmanager
from threading import RLock
from urllib.parse import quote_plus

import sqlalchemy as sa
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy_utils import create_database, database_exists, drop_database

from ._timing import SqlalchemyConnectionTiming, TimingValue

LOG = logging.getLogger(__name__)


class SqlalchemyConnection:
    def __init__(
        self,
        *,
        db_type: str,
        db_name: str,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: int,
        pool_size: int = 5,
        pool_overflow: int = 0,
        pool_recycle: int = 600,
        pool_timeout: int = 10,
        echo_query: bool = False,
        echo_pool: bool = False,
    ):
        self._db_type = db_type
        self._db_user = db_user
        self._db_password = db_password
        self._db_host = db_host
        self._db_port = db_port
        self._db_name = db_name

        self._pool_size = pool_size
        self._pool_overflow = pool_overflow
        self._pool_recycle = pool_recycle
        self._pool_timeout = pool_timeout

        self._echo_query = echo_query
        self._echo_pool = echo_pool

        self._engine = None
        self._lock = RLock()
        self._timing = SqlalchemyConnectionTiming()

        self.url = self._get_url()

    def _get_url(self):
        url_getter = {
            "mysql": self._get_mysql_url,
            "postgresql": self._get_postgresql_url,
        }.get(self._db_type)
        if not url_getter:
            raise ValueError("not support db_type {}".format(self._db_type))
        return url_getter()

    @property
    def timing(self) -> TimingValue:
        return self._timing.value

    def reset_timing(self):
        self._timing.reset()

    def _get_mysql_url(self):
        return "mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4".format(
            user=self._db_user,
            password=quote_plus(self._db_password),
            host=self._db_host,
            port=self._db_port,
            name=self._db_name,
        )

    def _get_postgresql_url(self):
        return "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}".format(
            user=self._db_user,
            password=quote_plus(self._db_password),
            host=self._db_host,
            port=self._db_port,
            name=self._db_name,
        )

    def is_database_exists(self) -> bool:
        return database_exists(self.url)

    def get_table_names(self) -> typing.List[str]:
        """
        Return all existed table names database.
        """
        inspector: Inspector = sa.inspect(self.get_engine())
        return list(inspector.get_table_names())

    def _sql_quote(self, value: str) -> str:
        return self.get_engine().dialect.identifier_preparer.quote(value)

    def create_database(self):
        """create database if not exists"""
        if not self.is_database_exists():
            encoding_map = {"mysql": "utf8mb4", "postgresql": "utf8"}
            create_database(self.url, encoding=encoding_map[self._db_type])

    def drop_database(self):
        """drop database if exists"""
        if self.is_database_exists():
            drop_database(self.url)

    def drop_all_tables(self):
        """drop all tables in the database if exists"""
        if self.is_database_exists():
            with self.atomic() as db:
                for table in self.get_table_names():
                    sql = "DROP TABLE {}".format(self._sql_quote(table))
                    db.execute(sql)

    def clear_database(self):
        """delete all records in the database"""
        if self.is_database_exists():
            with self.atomic() as db:
                for table in self.get_table_names():
                    sql = "TRUNCATE TABLE {}".format(self._sql_quote(table))
                    db.execute(sql)

    def _create_engine(self) -> Engine:
        # https://docs.sqlalchemy.org/en/13/core/pooling.html
        engine: Engine = sa.create_engine(
            self.url,
            pool_pre_ping=False,
            pool_size=self._pool_size,
            max_overflow=self._pool_overflow,
            pool_timeout=self._pool_timeout,
            pool_recycle=self._pool_recycle,
            echo=self._echo_query,
            echo_pool=self._echo_pool,
        )
        sa.event.listen(
            engine, "before_cursor_execute", self._before_cursor_execute
        )
        return engine

    def _before_cursor_execute(self, *args, **kwargs):
        self._timing.increase_count()

    def get_engine(self) -> Engine:
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    self._engine = self._create_engine()
        return self._engine

    def close(self):
        with self._lock:
            if self._engine is not None:
                self._engine.dispose()
                self._engine = None

    @contextmanager
    def connect(self) -> typing.Iterator[Connection]:
        with self.get_engine().connect() as conn:
            yield conn

    @contextmanager
    def atomic(self) -> typing.Iterator[Connection]:
        start_time = time.time()
        try:
            with self.connect() as conn:
                with conn.begin():
                    yield conn
        finally:
            self._timing.increase_cost(time.time() - start_time)

    def check(self) -> bool:
        try:
            with self.atomic() as db:
                db.execute("select 1").scalar()
        except Exception as ex:
            LOG.info(f"SQL connection check failed: {ex}", exc_info=ex)
            return False
        return True
