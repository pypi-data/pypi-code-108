from logging.config import fileConfig

import sqlalchemy as sa
from alembic import context

from eztea.sql._connection import SqlalchemyConnection


class AlembicEnvPy:
    def __init__(
        self,
        metadata: sa.MetaData,
        connection: SqlalchemyConnection,
        **kwargs,
    ) -> None:
        self._metadata = metadata
        self._connection = connection
        self._kwargs = kwargs

    def run_migrations_offline(self):
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.
        """
        context.configure(
            url=self._connection.url,
            target_metadata=self._metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            **self._kwargs,
        )
        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online(self):
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.
        """
        with self._connection.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=self._metadata,
                **self._kwargs,
            )
            with context.begin_transaction():
                context.run_migrations()

    def run_if_alembic(self):
        # this is the Alembic Config object, which provides
        # access to the values within the .ini file in use.
        config = getattr(context, "config", None)
        if config is None:
            return
        # Interpret the config file for Python logging.
        # This line sets up loggers basically.
        fileConfig(config.config_file_name)
        if context.is_offline_mode():
            self.run_migrations_offline()
        else:
            self.run_migrations_online()
