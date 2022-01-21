from datetime import datetime
from functools import wraps
import asyncpg
from json import dumps, loads
from typing import Any, Callable, Dict, List, Optional

from fact_explorer.config import get_configuration, get_logger


async def _dict_converter(results: Any) -> List[Dict[str, Any]]:
    return [
        {"header": loads(item["header"]), "payload": loads(item["payload"])}
        for item in results
    ]


async def _extract_timestamp(record: Any) -> datetime:
    return datetime.fromtimestamp(int(str(loads(record["header"])["meta"]["_ts"])[:10]))


class Database:
    def __init__(self) -> None:
        self.config = get_configuration()
        self._cursor = None
        self.log = get_logger(self.__class__.__name__)

        self._connection_pool: asyncpg.Pool = None

    def connect_wrapper(func: Callable) -> Callable:  # type: ignore
        @wraps(func)
        async def wrapped(self, *args, **kwargs):  # noqa: ANN
            if not self._connection_pool:
                await self.connect()
            else:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    self.log.exception(e)

        return wrapped

    async def connect(self) -> None:
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                    host=self.config.database_host,
                    port=self.config.database_port,
                    user=self.config.database_user,
                    password=self.config.database_password,
                    database=self.config.database_name,
                )

            except Exception as e:
                self.log.exception(e)

    @connect_wrapper
    async def fetch_by_example(
        self,
        *,
        header_example: Optional[Dict[str, str]] = None,
        payload_example: Optional[Dict[str, str]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        if not header_example:
            header_example = {}
        if not payload_example:
            payload_example = {}

        con = await self._connection_pool.acquire()

        try:
            stmt = await con.prepare(  # type: ignore
                (
                    "select *"
                    " from fact"
                    " where header @> cast($1 as jsonb)"
                    " and payload @> cast ($2 as jsonb)"
                    " order by ser desc"
                    " limit $3::int"
                    " offset $4::int"
                )
            )
            self.log.debug(stmt.get_query())
            result = await stmt.fetch(
                dumps(header_example), dumps(payload_example), limit, offset
            )
            return await _dict_converter(result)
        finally:
            await self._connection_pool.release(con)

    @connect_wrapper
    async def fetch_by_time(self, *, until: datetime) -> List[Dict[str, Any]]:
        """
        Will fetch the entries up to approximately until. Will fetch at least 50 rows
        iff available. Will fetch in batches afterwards. Since factcast does not have
        an index on _ts this is faster than a FTS although of course less than ideal
        """
        result = []
        con = await self._connection_pool.acquire()

        try:
            async with con.transaction():  # type: ignore
                cursor = await con.cursor("select *" " from fact" " order by ser desc")  # type: ignore
                result += await cursor.fetch(50)
                last_retrieved_time = await _extract_timestamp(record=result[-1])
                while last_retrieved_time > until:
                    # Doing this by fetching rows. it is way faster than a FTS.
                    result += await cursor.fetch(50)
                    last_retrieved_time = await _extract_timestamp(record=result[-1])
                return await _dict_converter(result)
        finally:
            await self._connection_pool.release(con)


db_instance = Database()
