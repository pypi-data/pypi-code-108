from contextlib import asynccontextmanager
from typing import AsyncGenerator

from context_handler import AsyncContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from souswift_core.providers.database.base import DatabaseProvider


class SessionProvider(DatabaseProvider):
    def get_session(self):
        return sessionmaker(
            bind=self.engine, expire_on_commit=False, class_=AsyncSession
        )()

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.get_session() as session:   # type: AsyncSession
            async with session.begin():
                yield session

    @staticmethod
    def is_closed(client: AsyncSession):
        return not client.is_active

    @staticmethod
    async def close_client(client: AsyncSession):
        await client.close()

    async def health_check(self):
        async with self.acquire() as session:
            await session.execute(text('SELECT 1'))
        self.logger.info('Database Connection succeeded')

    Context = AsyncContext[AsyncSession]
