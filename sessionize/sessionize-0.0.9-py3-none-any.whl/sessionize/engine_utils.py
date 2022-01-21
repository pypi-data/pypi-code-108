from typing import Optional

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm.decl_api import DeclarativeMeta


def primary_keys(table: sa.Table) -> list[sa.Column]:
    """
    Given SqlAlchemy Table, query database for
    columns with primary key constraint.
    Returns a list of SqlAlchemy Columns.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    
    Returns
    -------
    list of SqlAlchemy Column objects with primary keys.
    """
    return table.primary_key.columns.values()


def has_primary_key(table: sa.Table) -> bool:
    """
    Given a SqlAlchemy Table, query database to
    check for primary keys.
    Returns True if table has primary key,
    False if no primary key.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    
    Returns
    -------
    bool
    """
    return len(primary_keys(table)) != 0


def get_table(
    name: str,
    engine: sa.engine.Engine,
    schema: Optional[str] = None
) -> sa.Table:
    """
    Maps a SqlAlchemy Table to a sql table.
    Returns SqlAlchemy Table object.
    
    Parameters
    ----------
    name: str
        name of sql table to map.
    engine: SqlAlchemy engine
        engine used to connect to sql database.
    schema: str, default None
        Database schema name.
    
    Returns
    -------
    A SqlAlchemy ORM Table object.
    """
    metadata = sa.MetaData(bind=engine, schema=schema)
    return sa.Table(name, metadata, autoload=True,
                    autoload_with=engine, schema=schema)


def get_class(
    name: str,
    engine: sa.engine.Engine,
    schema: Optional[str] = None
) -> DeclarativeMeta:
    """
    Maps a SqlAlchemy table class to a sql table.
    Returns the mapped class object.
    Some SqlAlchemy functions require the class
    instead of the table object.
    Will fail to map if sql table has no primary key.
    
    Parameters
    ----------
    name: str
        name of sql table to map.
    engine: sa.engine.Engine
        engine used to connect to sql database.
    schema: str, default None
        Database schema name.
    
    Returns
    -------
    A SqlAlchemy table class object.
    """
    metadata = sa.MetaData(engine, schema=schema)
    metadata.reflect(engine, only=[name])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    return Base.classes[name]


def get_column(table: sa.Table, column_name: str) -> sa.Column:
    return table.c[column_name]


