from context_handler import context_factory
from context_handler._datastructures import AbstractAsyncContextFactory  # noqa
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from .connection import ConnectionProvider
from .session import SessionProvider

session_factory: AbstractAsyncContextFactory[
    AsyncSession
] = context_factory(  # noqa
    SessionProvider, SessionProvider.Context
)
connection_factory: AbstractAsyncContextFactory[
    AsyncConnection
] = context_factory(  # noqa
    ConnectionProvider, ConnectionProvider.Context
)
