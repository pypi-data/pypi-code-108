"""Module to manage resource items in a PostgreSQL database."""

import asyncio
import asyncpg
import contextvars
import dataclasses
import fondat.codec
import fondat.error
import fondat.sql
import functools
import json
import logging
import typing
import uuid

from collections.abc import AsyncIterator, Iterable, Sequence
from contextlib import asynccontextmanager
from datetime import date, datetime
from decimal import Decimal
from fondat.data import datacls
from fondat.sql import Statement
from fondat.types import is_subclass
from fondat.validation import validate_arguments
from typing import Annotated, Any, Literal, Optional, Union
from uuid import UUID


_logger = logging.getLogger(__name__)

NoneType = type(None)


class PostgreSQLCodec(fondat.codec.Codec[fondat.codec.F, Any]):
    """Base class for PostgreSQL codecs."""


codec_providers = []


@functools.cache
def get_codec(python_type) -> PostgreSQLCodec:
    """Return a codec compatible with the specified Python type."""

    if typing.get_origin(python_type) is typing.Annotated:
        python_type = typing.get_args(python_type)[0]  # strip annotation

    for provider in codec_providers:
        if (codec := provider(python_type)) is not None:
            return codec

    raise TypeError(f"failed to provide PostgreSQL codec for {python_type}")


def _codec_provider(wrapped=None):
    if wrapped is None:
        return functools.partial(_codec_provider)
    codec_providers.append(wrapped)
    return wrapped


def _pass_codec(python_type, sql_type):
    class PassCodec(PostgreSQLCodec[python_type]):
        def __init__(self):
            self.python_type = python_type
            self.sql_type = sql_type

        @validate_arguments
        def encode(self, value: python_type) -> python_type:
            return value

        @validate_arguments
        def decode(self, value: python_type) -> python_type:
            return value

    return PassCodec()


_pass_codecs = []


def _add_pass_codec(python_type, sql_type):
    _pass_codecs.append(_pass_codec(python_type, sql_type))


# order is significant
_add_pass_codec(str, "text")
_add_pass_codec(bool, "boolean")
_add_pass_codec(int, "bigint")
_add_pass_codec(float, "double precision")
_add_pass_codec(bytes, "bytea")
_add_pass_codec(bytearray, "bytea")
_add_pass_codec(UUID, "uuid")
_add_pass_codec(Decimal, "numeric")
_add_pass_codec(datetime, "timestamp with time zone")
_add_pass_codec(date, "date")


@_codec_provider
def pass_provider(python_type):
    for codec in _pass_codecs:
        if is_subclass(python_type, codec.python_type):
            return codec


@_codec_provider
def _iterable_codec_provider(python_type):

    origin = typing.get_origin(python_type)
    if not origin or not is_subclass(origin, Iterable):
        return

    args = typing.get_args(python_type)
    if not args or len(args) > 1:
        return

    codec = get_codec(args[0])

    class IterableCodec(PostgreSQLCodec[python_type]):

        sql_type = f"{codec.sql_type}[]"

        @validate_arguments
        def encode(self, value: python_type) -> Any:
            return [codec.encode(v) for v in value]

        @validate_arguments
        def decode(self, value: Any) -> python_type:
            return python_type(codec.decode(v) for v in value)

    return IterableCodec()


@_codec_provider
def _union_codec_provider(python_type):
    """
    Provides a codec that encodes/decodes a Union or Optional value to/from a
    compatible PostgreSQL value. For Optional value, will use codec for its
    type, otherwise it encodes/decodes as jsonb.
    """

    origin = typing.get_origin(python_type)
    if origin is not Union:
        return

    args = typing.get_args(python_type)
    is_nullable = NoneType in args
    args = [a for a in args if a is not NoneType]
    codec = (
        get_codec(args[0]) if len(args) == 1 else _jsonb_codec_provider(python_type)
    )  # Optional[T]

    class UnionCodec(PostgreSQLCodec[python_type]):

        sql_type = codec.sql_type

        @validate_arguments
        def encode(self, value: python_type) -> Any:
            if value is None:
                return None
            return codec.encode(value)

        @validate_arguments
        def decode(self, value: Any) -> python_type:
            if value is None and is_nullable:
                return None
            return codec.decode(value)

    return UnionCodec()


@_codec_provider
def _literal_codec_provider(python_type):
    """
    Provides a codec that encodes/decodes a Literal value to/from a compatible
    PostgreSQL value. If all literal values share the same type, then a codec
    for that type will be used, otherwise it encodes/decodes as jsonb.
    """

    origin = typing.get_origin(python_type)
    if origin is not Literal:
        return

    return get_codec(Union[tuple(type(arg) for arg in typing.get_args(python_type))])


@_codec_provider
def _jsonb_codec_provider(python_type):
    """
    Provides a codec that encodes/decodes a value to/from a PostgreSQL jsonb
    value. It unconditionally returns the codec, regardless of Python type.
    It must be the last provider in the list to serve as a catch-all.
    """

    json_codec = fondat.codec.get_codec(fondat.codec.JSON, python_type)

    class JSONBCodec(PostgreSQLCodec[python_type]):

        sql_type = "jsonb"

        @validate_arguments
        def encode(self, value: python_type) -> str:
            return json.dumps(json_codec.encode(value))

        @validate_arguments
        def decode(self, value: str) -> python_type:
            return json_codec.decode(json.loads(value))

    return JSONBCodec()


class _Results(AsyncIterator[Any]):
    def __init__(self, statement, results):
        self.statement = statement
        self.results = results
        self.codecs = {
            k: get_codec(t)
            for k, t in typing.get_type_hints(statement.result, include_extras=True).items()
        }

    def __aiter__(self):
        return self

    async def __anext__(self):
        row = await self.results.__anext__()
        result = {}
        for key in self.codecs:
            with fondat.codec.DecodeError.path_on_error(key):
                result[key] = self.codecs[key].decode(row[key])
        return self.statement.result(**result)


# fmt: off
@datacls
class Config:
    dsn: Annotated[Optional[str], "connection arguments in libpg connection URI format"]
    min_size: Annotated[Optional[int], "number of connections to initialize pool with"]
    max_size: Annotated[Optional[int], "maximum number of connections in the pool"]
    max_queries: Annotated[Optional[int], "number of queries before connection is replaced"]
    max_inactive_connection_lifetime: Annotated[Optional[float], "seconds after inactive connection closed"]
    host: Annotated[Optional[str], "database host address"]
    port: Annotated[Optional[int], "port number to connect to"]
    user: Annotated[Optional[str], "the name of the database role used for authentication"]
    password: Annotated[Optional[str], "password to be used for authentication"]
    passfile: Annotated[Optional[str], "the name of the file used to store passwords"]
    database: Annotated[Optional[str], "the name of the database to connect to"]
    timeout: Annotated[Optional[float], "connection timeout in seconds"]
    ssl: Optional[Literal["disable", "prefer", "require", "verify-ca", "verify-full"]]
# fmt: on


@asynccontextmanager
async def _async_null_context():
    yield


class Database(fondat.sql.Database):
    """
    Manages access to a PostgreSQL database.

    Supplied configuration can be a Config dataclass instance, or a function or coroutine
    function that returns a Config dataclass instance.
    """

    @classmethod
    async def create(cls, config: Config):
        self = cls()
        kwargs = {k: v for k, v in dataclasses.asdict(config).items() if v is not None}
        self._config = config
        self._pool = await asyncpg.create_pool(**kwargs)
        self._conn = contextvars.ContextVar("fondat_postgresql_conn", default=None)
        self._txn = contextvars.ContextVar("fondat_postgresql_txn", default=None)
        self._task = contextvars.ContextVar("fondat_postgresql_task", default=None)
        return self

    async def close(self):
        """Close all database connections."""
        if self._pool:
            await self._pool.close()
        self._pool = None

    @asynccontextmanager
    async def connection(self):
        task = asyncio.current_task()
        if self._conn.get() and self._task.get() is task:
            yield  # connection already established
            return
        _logger.debug("open connection")
        self._task.set(task)
        async with self._pool.acquire(timeout=self._config.timeout) as connection:
            self._conn.set(connection)
            try:
                yield
            finally:
                _logger.debug("close connection")
                self._conn.set(None)

    @asynccontextmanager
    async def transaction(self):
        txid = uuid.uuid4().hex
        _logger.debug("transaction begin %s", txid)
        token = self._txn.set(txid)
        async with self.connection():
            connection = self._conn.get()
            transaction = connection.transaction()
            await transaction.start()

            async def commit():
                _logger.debug("transaction commit %s", txid)
                await transaction.commit()

            async def rollback():
                _logger.debug("transaction rollback %s", txid)
                await transaction.rollback()

            try:
                yield
            except GeneratorExit:  # explicit cleanup of asynchronous generator
                await commit()
            except Exception:
                await rollback()
                raise
            else:
                await commit()
            finally:
                self._txn.reset(token)

    async def execute(self, statement: Statement) -> Optional[AsyncIterator[Any]]:
        if not self._txn.get():
            raise RuntimeError("transaction context required to execute statement")
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(str(statement))
        text = []
        args = []
        for fragment in statement:
            if isinstance(fragment, str):
                text.append(fragment)
            else:
                args.append(get_codec(fragment.type).encode(fragment.value))
                text.append(f"${len(args)}")
        text = "".join(text)
        conn = self._conn.get()
        if statement.result is None:
            await conn.execute(text, *args)
        else:  # expecting a result
            return _Results(statement, conn.cursor(text, *args).__aiter__())

    def get_codec(self, python_type: Any) -> PostgreSQLCodec:
        return get_codec(python_type)


class Index(fondat.sql.Index):
    """
    Represents an index on a table in a PostgreSQL database.

    Parameters:
    • name: name of index
    • table: table that the index defined for
    • keys: index keys (typically column names with optional order)
    • unique: is index unique
    • method: indexing method
    """

    __slots__ = ("method",)

    def __init__(
        self,
        name: str,
        table: fondat.sql.Table,
        keys: Sequence[str],
        unique: bool = False,
        method: Optional[str] = None,
    ):
        super().__init__(name, table, keys, unique)
        self.method = method

    def __repr__(self):
        result = f"Index(name={self.name}, table={self.table}, keys={self.keys}, unique={self.unique} method={self.method})"

    async def create(self):
        """Create index in database."""
        stmt = Statement()
        stmt += "CREATE "
        if self.unique:
            stmt += "UNIQUE "
        stmt += f"INDEX {self.name} ON {self.table.name} "
        if self.method:
            stmt += f"USING {self.method} "
        stmt += "("
        stmt += ", ".join(self.keys)
        stmt += ");"
        await self.table.database.execute(stmt)
