import logging
from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.datastructures import State

from souswift_core.providers.config import DatabaseConfig


class DatabaseProvider(ABC):
    state_name = 'database_provider'

    def __init__(
        self, database_config: DatabaseConfig, logger: logging.Logger
    ) -> None:
        self.config = database_config
        self.logger = logger
        self.engine, self.sync_engine = self._create_engine()

    def _create_engine(self):
        return create_async_engine(
            self.config.get_uri(is_async=True), **self.config.pool_config
        ), create_engine(
            self.config.get_uri(is_async=False), **self.config.pool_config
        )

    @abstractmethod
    async def health_check(self):
        ...


def setup_database(
    provider_class: type[DatabaseProvider],
    config: DatabaseConfig,
    logger: logging.Logger,
):
    async def _setup_database(state: State):
        provider = provider_class(config, logger)
        setattr(
            state,
            DatabaseProvider.state_name,
            provider,
        )
        await provider.health_check()

    return _setup_database
