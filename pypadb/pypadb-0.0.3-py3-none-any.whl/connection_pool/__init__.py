from typing import Union

from dbutils.pooled_db import PooledDB, PooledDedicatedDBConnection, PooledSharedDBConnection

import exception

_POOL: PooledDB = None
_Cursor = None


def _init_pool(cursor, **data: dict):
    global _POOL, _Cursor
    _POOL = PooledDB(**data)
    _Cursor = cursor


def connection() -> Union[PooledSharedDBConnection, PooledDedicatedDBConnection]:
    if not _POOL:
        raise exception.PoolUninitializedException('connection pool uninitialized')
    return _POOL.connection()


def cursor_type():
    return _Cursor
