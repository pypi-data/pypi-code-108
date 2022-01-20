from contextlib import asynccontextmanager
from typing import AsyncGenerator

from context_handler import AsyncContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from souswift_core.providers.database.base import DatabaseProvider


class ConnectionProvider(DatabaseProvider):
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[AsyncConnection, None]:
        async with self.engine.begin() as connection:
            yield connection

    @staticmethod
    def is_closed(client: AsyncConnection):
        return client.closed

    @staticmethod
    async def close_client(client: AsyncConnection):
        await client.close()

    async def health_check(self):
        async with self.acquire() as connection:
            await connection.execute(text('SELECT 1'))
        self.logger.info('Database Connection succeeded')

    Context = AsyncContext[AsyncConnection]
