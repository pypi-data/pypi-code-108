from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.event import listen
from sqlalchemy.orm import sessionmaker

import shutil
import sqlite3
import tempfile


__all__ = ["ThreediDatabase"]


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Switch on legacy_alter_table setting to fix our migrations.

    Why?
    1) SQLite does not support "DROP COLUMN ...". You have to create a new table,
       copy the data, drop the old table, then rename. Luckily Alembic supports this pattern.
       They call it a "batch operation". See https://alembic.sqlalchemy.org/en/latest/batch.html.
    2) Newer SQLite drivers do a lot of fancy checks on a RENAME command. This made our
       "batch operations" fail in case a view referred to the table that is getting a "batch operation".
       The solution was a PRAGMA command. See https://www.sqlite.org/pragma.html#pragma_legacy_alter_table.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA legacy_alter_table=ON")
        # Some additional pragmas recommended in https://www.sqlite.org/security.html, paragraph 1.2
        cursor.execute("PRAGMA cell_size_check=ON")
        cursor.execute("PRAGMA mmap_size=0")
        cursor.close()


def load_spatialite(con, connection_record):
    """Load spatialite extension as described in
    https://geoalchemy-2.readthedocs.io/en/latest/spatialite_tutorial.html"""
    import sqlite3

    con.enable_load_extension(True)
    cur = con.cursor()
    libs = [
        # SpatiaLite >= 4.2 and Sqlite >= 3.7.17, should work on all platforms
        ("mod_spatialite", "sqlite3_modspatialite_init"),
        # SpatiaLite >= 4.2 and Sqlite < 3.7.17 (Travis)
        ("mod_spatialite.so", "sqlite3_modspatialite_init"),
        # SpatiaLite < 4.2 (linux)
        ("libspatialite.so", "sqlite3_extension_init"),
    ]
    found = False
    for lib, entry_point in libs:
        try:
            cur.execute("select load_extension('{}', '{}')".format(lib, entry_point))
        except sqlite3.OperationalError:
            continue
        else:
            found = True
            break
    if not found:
        raise RuntimeError("Cannot find any suitable spatialite module")
    cur.close()
    con.enable_load_extension(False)


class ThreediDatabase:
    def __init__(self, connection_settings, db_type="spatialite", echo=False):
        """

        :param connection_settings:
        db_type (str choice): database type. 'sqlite' and 'postgresql' are
                              supported
        """
        self.settings = connection_settings
        self.db_type = db_type
        self.echo = echo

        self._engine = None
        self._base_metadata = None

    @property
    def engine(self):
        return self.get_engine()

    @property
    def base_path(self):
        if self.db_type == "spatialite":
            return Path(self.settings["db_path"]).absolute().parent

    def get_engine(self, get_seperate_engine=False):

        if self._engine is None or get_seperate_engine:
            if self.db_type == "spatialite":
                engine = create_engine(
                    "sqlite:///{0}".format(self.settings["db_path"]), echo=self.echo
                )
                listen(engine, "connect", load_spatialite)
                if get_seperate_engine:
                    return engine
                else:
                    self._engine = engine

            elif self.db_type == "postgres":
                con = (
                    "postgresql://{username}:{password}@{host}:"
                    "{port}/{database}".format(**self.settings)
                )

                engine = create_engine(con, echo=self.echo)
                if get_seperate_engine:
                    return engine
                else:
                    self._engine = engine

        return self._engine

    def get_session(self, **kwargs):
        """Get a SQLAlchemy session for optimal control.

        It is probably necessary to call ``session.commit``, ``session.rollback``
        and/or ``session.close``.

        See also:
          https://docs.sqlalchemy.org/en/13/orm/session_basics.html
        """
        return sessionmaker(bind=self.engine)(**kwargs)

    @contextmanager
    def session_scope(self, **kwargs):
        """Get a session to execute a single transaction in a "with as" block."""
        session = self.get_session(**kwargs)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def file_transaction(self, **kwargs):
        """Copy the complete database into a tmpdir and work on that one.

        On contextmanager exit, the database is copied back and the real
        database is overwritten. On error, nothing happens.
        """
        if self.db_type != "spatialite":
            raise NotImplementedError(
                f"Cannot make database backups for db_type {self.db_type}"
            )
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as work_file:
            # copy the database to the temporary directory
            shutil.copy(self.settings["db_path"], work_file.name)
            # yield a new ThreediDatabase refering to the backup
            yield self.__class__({"db_path": work_file.name}, "spatialite")
            # this is only reached if there was no error:
            shutil.copy(work_file.name, self.settings["db_path"])

    def check_connection(self):
        """Check if there a connection can be started with the database

        :return: True if a connection can be established, otherwise raises an
            appropriate error.
        """
        session = self.get_session()
        r = session.execute("select 1")
        return r.fetchone()

    def check_integrity(self):
        """Should be called before doing anything with an untrusted sqlite file."""
        with self.session_scope() as session:
            session.execute("PRAGMA integrity_check")
