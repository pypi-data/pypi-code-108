from .errors import MigrationMissingError
from .threedi_model import constants
from .threedi_model import models
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table

import warnings


__all__ = ["ModelSchema"]


def get_alembic_config(connection=None):
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "threedi_modelchecker:migrations")
    alembic_cfg.set_main_option("version_table", constants.VERSION_TABLE_NAME)
    if connection is not None:
        alembic_cfg.attributes["connection"] = connection
    return alembic_cfg


def get_schema_version():
    """Returns the version of the schema in this library"""
    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)
    with EnvironmentContext(config=config, script=script) as env:
        return int(env.get_head_revision())


def _upgrade_database(db, revision="head"):
    """Upgrade ThreediDatabase instance"""
    with db.get_engine().begin() as connection:
        config = get_alembic_config(connection)
        script = ScriptDirectory.from_config(config)

        def upgrade(rev, context):
            return script._upgrade_revs(revision, rev)

        with EnvironmentContext(
            config,
            script,
            fn=upgrade,
            destination_rev=revision,
            version_table=constants.VERSION_TABLE_NAME,
        ):
            script.run_env()


class ModelSchema:
    def __init__(self, threedi_db, declared_models=models.DECLARED_MODELS):
        self.db = threedi_db
        self.declared_models = declared_models

    def _get_version_old(self):
        """The version of the database using the old 'south' versioning."""
        south_migrationhistory = Table(
            "south_migrationhistory", MetaData(), Column("id", Integer)
        )
        engine = self.db.get_engine()
        if not engine.has_table("south_migrationhistory"):
            return
        with engine.connect() as connection:
            query = south_migrationhistory.select().order_by(
                south_migrationhistory.columns["id"].desc()
            )
            versions = list(connection.execute(query.limit(1)))
            if len(versions) == 1:
                return versions[0][0]
            else:
                return None

    def get_version(self):
        """Returns the id (integer) of the latest migration"""
        with self.db.get_engine().connect() as connection:
            context = MigrationContext.configure(
                connection, opts={"version_table": constants.VERSION_TABLE_NAME}
            )
            version = context.get_current_revision()

        if version is not None:
            return int(version)
        else:
            return self._get_version_old()

    def upgrade(self, revision="head", backup=True):
        """Upgrade the database to the latest version.

        This requires either a completely empty database or a database with its
        current schema version at least 174 (the latest migration of the old
        model databank).

        The upgrade is done using database transactions. However, for SQLite,
        database transactions are only partially supported. To ensure that the
        database file does not become corrupt, enable the "backup" parameter.
        If the database is temporary already (or if it is PostGIS), disable
        it.
        """
        v = self.get_version()
        if v is not None and v < constants.LATEST_SOUTH_MIGRATION_ID:
            raise MigrationMissingError(
                f"The modelchecker cannot update versions below "
                f"{constants.LATEST_SOUTH_MIGRATION_ID}. Please consult the "
                f"3Di documentation on how to update legacy databases."
            )
        if backup:
            with self.db.file_transaction() as work_db:
                _upgrade_database(work_db, revision=revision)
        else:
            _upgrade_database(self.db, revision=revision)

    def validate_schema(self):
        """Very basic validation of 3Di schema.

        Check that the database has the latest migration applied. If the
        latest migrations is applied, we assume the database also contains all
        tables and columns defined in threedi_model.models.py.

        :return: True if the threedi_db schema is valid, raises an error otherwise.
        :raise MigrationMissingError, MigrationTooHighError
        """
        version = self.get_version()
        if version is None or version < constants.MIN_SCHEMA_VERSION:
            raise MigrationMissingError(
                f"The modelchecker requires at least schema version "
                f"{constants.MIN_SCHEMA_VERSION}. Current version: {version}."
            )

        schema_version = get_schema_version()
        if version > schema_version:
            warnings.warn(
                f"The database version is higher than the modelchecker "
                f"({version} > {schema_version}). This may lead to unexpected "
                f"results. "
            )
        return True

    def get_missing_tables(self):
        pass

    def get_missing_columns(self):
        pass
