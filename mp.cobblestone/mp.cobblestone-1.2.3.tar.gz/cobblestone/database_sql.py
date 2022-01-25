# -----------------------------------------------------------------------
# Copyright 2020 Mina Pêcheux

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at the root of the repo.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------

import os
import urllib.parse
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import cobblestone.models as all_schemas
from cobblestone.helpers.converters import wrap_additional_fields

SQL_TYPE = os.getenv('DB_SUBTYPE', 'sqlite')
SQL_USER = os.getenv('DB_USER')
SQL_PASSWORD = os.getenv('DB_PASSWORD')
SQL_NAME = os.getenv('DB_NAME')
SQL_HOST = os.getenv('DB_HOST', '0.0.0.0')
sql_port_str = os.getenv('DB_PORT', '3306')
SQL_PORT = int(sql_port_str) if len(sql_port_str) > 0 else None

connect_args = {}
engine_args = {'echo': False}

db_url = ''
if SQL_TYPE == 'sqlite':
    # if no Sqlite database name is given, use the :memory: database
    if SQL_NAME == '':
        db_url = 'sqlite://'
    # else the database name is actually the database file path on the system
    # (including the extension)
    else:
        db_url = f'sqlite:///{SQL_NAME}'

    # only needed for Sqlite
    connect_args['check_same_thread'] = False

    print(f'Connecting to Sqlite database ({db_url})')
elif SQL_TYPE == 'mysql' and SQL_PORT is not None:
    SQL_PASSWORD = urllib.parse.quote_plus(SQL_PASSWORD)
    db_url = f'mysql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_NAME}'

    engine_args['pool_recycle'] = 3600

    print(f'Connecting to MySQL database ({db_url})')
elif SQL_TYPE == 'postgres' and SQL_PORT is not None:
    SQL_PASSWORD = urllib.parse.quote_plus(SQL_PASSWORD)
    db_url = f'postgresql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_NAME}'

    engine_args['pool_recycle'] = 3600

    print(f'Connecting to PostgreSQL database ({db_url})')

if db_url == '':
    print('Error: could not initialize database connection. Exiting.')
    import sys
    sys.exit(1)

db = create_engine(
    db_url,
    connect_args=connect_args,
    **engine_args)
Session = sessionmaker(bind=db)

Base = declarative_base()


def initialize_database_metadata():
    from cobblestone.helpers.converters import DIRECT_TABLES
    from cobblestone.helpers.converters import ASSOCIATION_TABLES
    Base.metadata.create_all(db)
    wrap_additional_fields(all_schemas.__all__)


@contextmanager
def session_scope(autocommit=True):
    session = Session()
    try:
        yield session
        if autocommit:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
