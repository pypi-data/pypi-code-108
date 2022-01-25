import logging
import re
import subprocess

import psycopg2.errorcodes
import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from puddl.conf import DBConfig
from puddl.exc import DBException

log = logging.getLogger(__package__)


class DB:
    """
    >>> db = DB('test')

    This creates a Postgres ROLE and SCHEMA with the name "sunrise".

    Please instantiate this class once per process, because it uses SQLAlchemy's engine,
    thus similar rules apply. "[...] the Engine is most efficient when created just once
    at the module level of an application, not per-object or per-function call"
    -- https://docs.sqlalchemy.org/en/13/core/connections.html#basic-usage

    An app holds DB configuration and an engine:

    >>> db.db_config
    DBConfig('sunrise')
    >>> db.engine
    Engine(postgresql://sunrise:***@localhost:13370/puddl?application_name=sunrise)
    """

    name: str
    db_config: DBConfig
    engine: Engine

    def __init__(self, name):
        log.debug(f'initializing DB({repr(name)})')
        self.name = name

        if self.name is None:
            self.db_config = DBConfig()
        else:
            # https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
            if re.match(r'[_a-z][a-z0-9]*', name) is None:
                raise DBException('Invalid DB name')
            # our config is solely based on "name"
            self.db_config = DBConfig(name)
            self._init_named_database(self.db_config)

        self.engine = sqlalchemy.create_engine(self.db_config.url)
        session_cls = sessionmaker(self.engine)
        self.session = session_cls()
        self.autocommit_engine = self.engine.execution_options(isolation_level="AUTOCOMMIT")

    @staticmethod
    def _init_named_database(db_config: DBConfig):
        x = db_config
        # get global credentials (to upsert the app itself)
        root_db_config = DBConfig()
        # CREATE DATABASE only works in Postgres' AUTOCOMMIT mode
        root_engine = sqlalchemy.create_engine(root_db_config.url, isolation_level="AUTOCOMMIT")
        # https://docs.sqlalchemy.org/en/14/core/connections.html#using-transactions
        with root_engine.connect() as root_conn:
            log.debug(f'creating role {x.PGUSER}')
            root_conn.execute(sqlalchemy.func.puddl_upsert_role(x.PGUSER, x.PGPASSWORD))
            log.debug(f'the role "puddl" is part of the role {x.PGUSER}')
            root_conn.execute(f"GRANT {x.PGUSER} TO puddl")
            try:
                log.debug(f'creating database {x.PGDATABASE}')
                root_conn.execute(f"CREATE DATABASE {x.PGDATABASE} WITH OWNER {x.PGUSER}")
            except ProgrammingError as e:
                if e.orig.pgcode == psycopg2.errorcodes.DUPLICATE_DATABASE:
                    log.debug(f'database {x.PGDATABASE} already exists')
                    pass
                else:
                    raise

    def has_table(self, table_name):
        return inspect(self.engine).has_table(table_name)

    def df_dump(self, df, table_name, index=True, drop_cascade=False):
        """
        Dumps a DataFrame to table_name.
        WARNING! This replaces the table if it exists.
        """
        if drop_cascade:
            self.engine.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')
        if index:
            # follow SQL conventions for the index
            df.index += 1
        return df.to_sql(table_name, self.engine, if_exists='replace', index=index)

    def df_append(self, df, table_name: str, index=True):
        if index:
            # follow SQL conventions for the index
            df.index += 1
        return df.to_sql(table_name, self.engine, if_exists='append', index=index)

    def psql(self):
        db_env = self.db_config
        subprocess.Popen('psql', env=db_env).wait()
