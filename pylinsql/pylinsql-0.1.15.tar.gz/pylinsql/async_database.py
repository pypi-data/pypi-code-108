"""
SQL database connection handling with the async/await syntax.
"""

from __future__ import annotations

import dataclasses
import logging
import os
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import (
    Any,
    AsyncIterator,
    ClassVar,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import asyncpg

from .base import DataClass, cast_if_not_none, is_dataclass_instance
from .core import DEFAULT, is_dataclass_type
from .query import insert_or_select, select

T = TypeVar("T")


@dataclasses.dataclass(eq=True, frozen=True)
class ConnectionParameters:
    "Encapsulates database connection parameters."

    user: str = dataclasses.field(
        default_factory=lambda: os.getenv("PSQL_USERNAME", "postgres")
    )
    password: str = dataclasses.field(
        default_factory=lambda: os.getenv("PSQL_PASSWORD", "")
    )
    database: str = dataclasses.field(
        default_factory=lambda: os.getenv("PSQL_DATABASE", "postgres")
    )
    host: str = dataclasses.field(
        default_factory=lambda: os.getenv("PSQL_HOSTNAME", "localhost")
    )
    port: int = dataclasses.field(
        default_factory=lambda: int(os.getenv("PSQL_PORT", "5432"))
    )
    command_timeout: int = 60
    schema: str = dataclasses.field(
        default_factory=lambda: os.getenv("PSQL_SCHEMA", "public")
    )

    def as_kwargs(self) -> Dict[str, Union[str, int]]:
        "Connection string parameters as keyword arguments."

        d = dataclasses.asdict(self)
        del d["schema"]
        return d


class DatabasePool:
    """
    A pool of connections to a database server.

    Connection pools can be used to manage a set of connections to the database. Connections are first acquired
    from the pool, then used, and then released back to the pool.
    """

    pool: asyncpg.pool.Pool

    def __init__(self, pool):
        self.pool = pool

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[DatabaseConnection]:
        conn = await self.pool.acquire()
        try:
            yield DatabaseConnection(conn)
        finally:
            await self.pool.release(conn)

    async def release(self) -> None:
        "Close all connections in the pool."

        return await self.pool.close()


class SchemaConnection(asyncpg.Connection):
    "An asyncpg connection that automatically establishes a default schema (search path)."

    default_schema: ClassVar[str]
    initialized: bool = False

    def __init_subclass__(cls, /, default_schema, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.default_schema = default_schema

    async def _initialize(self) -> None:
        if not self.initialized:
            await super().execute(
                f"SET SESSION search_path TO '{type(self).default_schema}'"
            )
            self.initialized = True

    async def prepare(self, query, *, timeout=None, record_class=None):
        await self._initialize()
        return await super().prepare(query, timeout=timeout, record_class=record_class)

    async def execute(self, query: str, *args, timeout: float = None) -> str:
        await self._initialize()
        logging.debug(query)
        return await super().execute(query, *args, timeout=timeout)

    async def executemany(self, command: str, args, *, timeout: float = None):
        await self._initialize()
        logging.debug(command)
        return await super().executemany(command, args, timeout=timeout)


def _get_connection_type(params: ConnectionParameters) -> SchemaConnection:
    class_name = f"Connection{hash(params)}"
    class_type = type(class_name, (SchemaConnection,), {}, default_schema=params.schema)
    return class_type


async def _create_connection(params: ConnectionParameters) -> asyncpg.Connection:
    return await asyncpg.connect(
        connection_class=_get_connection_type(params), **params.as_kwargs()
    )


async def _create_pool(params: ConnectionParameters) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        min_size=1,
        max_size=8,
        connection_class=_get_connection_type(params),
        **params.as_kwargs(),
    )


@asynccontextmanager
async def pool(
    params: ConnectionParameters = None,
) -> AsyncIterator[DatabasePool]:
    "Creates a connection pool."

    if params is None:
        params = ConnectionParameters()
    pool = await _create_pool(params)
    try:
        yield DatabasePool(pool)
    finally:
        await pool.close()
        pool.terminate()


class DatabaseClient:
    conn: asyncpg.Connection

    def __init__(self, conn):
        self.conn = conn

    @staticmethod
    def _unwrap_one(target_type: Type[T], record: asyncpg.Record) -> Optional[T]:
        "Converts a result record into the expected type."

        if record is None:
            return None

        if target_type is None:
            if len(record) > 1:
                return tuple(record.values())
            else:
                return record[0]

        elif is_dataclass_type(target_type):
            # initialize data class with parameters taken from query result
            return target_type(*record.values())

        elif target_type is list or target_type is set or target_type is tuple:
            # initialize collection class with iterator
            return target_type(record.values())

        else:
            raise TypeError(f"unsupported target type {target_type}")

    @staticmethod
    def _unwrap_all(target_type: Type[T], records: List[asyncpg.Record]) -> List[T]:
        "Converts a list of records into a list of the expected type."

        if not records:
            return []

        if target_type is None:
            head = records[0]
            if len(head) > 1:
                return [tuple(record.values()) for record in records]
            else:
                return [record[0] for record in records]

        elif is_dataclass_type(target_type):
            # initialize data class with parameters taken from query result
            return [target_type(*record.values()) for record in records]

        elif isinstance(target_type, (list, tuple, set)):
            # initialize collection class with iterator
            return [target_type(record.values()) for record in records]

        else:
            raise TypeError(f"unsupported target type {target_type}")

    async def select_first(
        self, sql_generator_expr: Generator[T, None, None], *args
    ) -> T:
        "Returns the first row of the resultset produced by a SELECT query."

        query = select(sql_generator_expr)
        stmt = await self.conn.prepare(str(query))
        logging.debug("executing query: %s", query)
        record: asyncpg.Record = await stmt.fetchrow(*args)
        return self._unwrap_one(query.typ, record)

    async def select(
        self, sql_generator_expr: Generator[T, None, None], *args
    ) -> List[T]:
        "Returns all rows of the resultset produced by a SELECT query."

        query = select(sql_generator_expr)
        stmt = await self.conn.prepare(str(query))
        logging.debug("executing query: %s", query)
        records: List[asyncpg.Record] = await stmt.fetch(*args)
        return self._unwrap_all(query.typ, records)

    async def insert_or_select(
        self,
        insert_obj: DataClass[T],
        sql_generator_expr: Generator[T, None, None],
        *args,
    ) -> T:
        "Queries the database and inserts a new row if the query returns an empty resultset."

        query = insert_or_select(insert_obj, sql_generator_expr)
        stmt = await self.conn.prepare(str(query))

        # append parameters for SELECT part
        fetch_args = list(args)

        # append parameters for INSERT part
        fields = dataclasses.fields(insert_obj)
        for field in fields:
            value = getattr(insert_obj, field.name)
            if value is not DEFAULT:
                fetch_args.append(value)

        logging.debug("executing query: %s", query)
        record: asyncpg.Record = await stmt.fetchrow(*fetch_args)
        return self._unwrap_one(query.typ, record)

    async def insert_or_ignore(self, insert_obj: DataClass[T]) -> None:

        if not is_dataclass_instance(insert_obj):
            raise TypeError(f"object to insert must be a dataclass instance")

        table_name = type(insert_obj).__name__
        fields = dataclasses.fields(insert_obj)

        column_list = []
        value_list = []
        for field in fields:
            value = getattr(insert_obj, field.name)
            if value is not DEFAULT:
                column_list.append(field.name)
                value_list.append(value)

        columns = ", ".join(column_list)
        placeholders = ", ".join(
            f"${index}" for index in range(1, len(column_list) + 1)
        )

        query = f"""INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"""
        logging.debug("executing query: %s", query)
        stmt = await self.conn.prepare(query)
        await stmt.executemany([value_list])

    async def typed_fetch(self, typ: T, query: str, *args) -> List[T]:
        """Maps all columns of a database record to a Python data class."""

        if not is_dataclass_type(typ):
            raise TypeError(f"{typ} must be a dataclass type")

        records = await self.conn.fetch(query, *args)
        return self._typed_fetch(typ, records)

    async def typed_fetch_column(
        self, typ: Type[T], query: str, *args, column: int = 0
    ) -> List[T]:
        """Maps a single column of a database record to a Python class."""

        records = await self.conn.fetch(query, *args)
        return [cast_if_not_none(typ, record[column]) for record in records]

    async def typed_fetch_value(
        self, typ: Type[T], query: str, *args, column: int = 0
    ) -> T:
        value = await self.conn.fetchval(query, *args, column=column)
        return cast_if_not_none(typ, value)

    def _typed_fetch(self, typ: Type[T], records: List[asyncpg.Record]) -> List[T]:
        results = []
        for record in records:
            result = object.__new__(typ)

            if is_dataclass_type(typ):
                for field in dataclasses.fields(typ):
                    key = field.name
                    value = record.get(key, None)
                    if value is not None:
                        setattr(result, key, value)
                    elif field.default:
                        setattr(result, key, field.default)
                    else:
                        raise RuntimeError(
                            f"object field {key} without default value is missing a corresponding database record column"
                        )
            else:
                for key, value in record.items():
                    setattr(result, key, value)

            results.append(result)
        return results

    async def raw_fetch(
        self, query: str, *args, timeout=None, record_class=None
    ) -> List[asyncpg.Record]:

        return await self.conn.fetch(
            query, *args, timeout=timeout, record_class=record_class
        )

    async def raw_fetchval(
        self, query: str, *args, column: int = 0, timeout: Optional[float] = None
    ) -> Any:
        return await self.conn.fetchval(query, *args, column=column, timeout=timeout)

    async def raw_execute(
        self, query: str, *args, timeout: Optional[float] = None
    ) -> str:
        return await self.conn.execute(query, *args, timeout=timeout)

    async def raw_executemany(
        self, command: str, args: Iterable, timeout: Optional[float] = None
    ) -> None:
        return await self.conn.executemany(command, args, timeout=timeout)


class DatabaseTransaction(DatabaseClient):
    def __init__(self, conn, transaction):
        super().__init__(conn)
        self.transaction = transaction


class DatabaseConnection(DatabaseClient):
    def __init__(self, conn):
        super().__init__(conn)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[DatabaseTransaction]:
        transaction = self.conn.transaction()
        await transaction.start()
        try:
            yield DatabaseTransaction(self.conn, transaction)
        except:
            await transaction.rollback()
            raise
        else:
            await transaction.commit()


@asynccontextmanager
async def connection(
    params: ConnectionParameters = None,
) -> AsyncIterator[DatabaseConnection]:
    if params is None:
        params = ConnectionParameters()
    conn = await _create_connection(params)
    try:
        yield DatabaseConnection(conn)
    finally:
        await conn.close()


_shared_pool = ContextVar("shared_pool", default={})


def _get_shared_pool() -> Dict[ConnectionParameters, DatabasePool]:
    """
    Returns a connection pool shared across the same asynchronous execution context.

    When an asynchronous task is called from another asynchronous task, the context is copied. However, only a shallow
    copy is made. We deliberately use a mutable object (a dictionary) as the context variable to ensure that changes
    made in child tasks are reflected in the parent (including the root ancestor) task. We assign a default value to
    the context variable such that the object spawns in the root ancestor task.

    As a result, a new connection pool is created for each set of connection parameters the first time a shared
    connection pool is requested. This connection pool is shared with all other asynchronous functions scheduled
    in the same asynchronous execution context.
    """

    return _shared_pool.get()


class SharedDatabasePool(DatabasePool):
    params: ConnectionParameters

    def __init__(self, pool: DatabasePool, params: ConnectionParameters):
        super().__init__(pool)
        self.params = params
        _get_shared_pool()[params] = self

    def __del__(self):
        _get_shared_pool().pop(self.params, None)

    @classmethod
    async def get_or_create(cls, params: ConnectionParameters) -> SharedDatabasePool:
        pool = _get_shared_pool().get(params, None)
        if pool is None:
            pool = SharedDatabasePool(await _create_pool(params), params)
        return pool

    async def release(self) -> None:
        _get_shared_pool().pop(self.params, None)
        return await super().release()


async def shared_pool(params: ConnectionParameters = None) -> DatabasePool:
    "A database connection pool shared across coroutines in the asynchronous execution context."

    if params is None:
        params = ConnectionParameters()

    return await SharedDatabasePool.get_or_create(params)


class DataAccess:
    params: ConnectionParameters

    def __init__(self, params: ConnectionParameters = None):
        self.params = ConnectionParameters() if params is None else params

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[DatabaseConnection]:
        pool = await shared_pool(self.params)
        async with pool.connection() as connection:
            yield connection
