from alembic import context
from sqlalchemy import create_engine
from threedi_modelchecker.threedi_model.models import Base

import os
import threedi_modelchecker.threedi_model.models  # NOQA needed for autogenerate


target_metadata = Base.metadata
config = context.config


def get_url():
    db_url = os.environ.get("DB_URL")
    if not db_url:
        raise RuntimeError(
            "Database URL must be specified using the environment variable DB_URL"
        )
    return db_url


def run_migrations_online():
    """Run migrations in 'online' mode.

    Note: SQLite does not (completely) support transactions, so, backup the
    SQLite before running migrations.
    """
    connectable = config.attributes.get("connection")
    if connectable is None:
        connectable = create_engine(get_url())

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise ValueError("Offline mode is not supported")
else:
    run_migrations_online()
