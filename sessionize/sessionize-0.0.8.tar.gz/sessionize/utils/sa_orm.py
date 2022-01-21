from typing import Optional, Union

import sqlalchemy as sa
from sqlalchemy.engine import Engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy.exc import PendingRollbackError

from sessionize.utils.custom_types import SqlConnection


def _get_table_name(
    table: Union[sa.Table, str]
) -> str:
    if isinstance(table, sa.Table):
        return table.name
    if isinstance(table, str):
        return table


def _get_table(
    table_name: Union[str, sa.Table],
    engine: Engine,
    schema: Optional[str] = None
) -> sa.Table:
    if isinstance(table_name, sa.Table):
        return table_name
    if isinstance(table_name, str):
        return get_table(table_name, engine, schema=schema)


def primary_keys(table: sa.Table) -> list[str]:
    """
    Given SqlAlchemy Table, query database for
    columns with primary key constraint.
    Returns a list of column names.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    
    Returns
    -------
    list of primary key names.
    """
    return [c.name for c in table.primary_key.columns.values()]


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
    connection: SqlConnection,
    schema: Optional[str] = None
) -> sa.Table:
    """
    Maps a SqlAlchemy Table to a sql table.
    Returns SqlAlchemy Table object.
    
    Parameters
    ----------
    name: str
        name of sql table to map.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    schema: str, default None
        Database schema name.
    
    Returns
    -------
    A SqlAlchemy mapped Table object.
    """
    metadata = sa.MetaData(bind=connection, schema=schema)

    if isinstance(connection, sa.orm.Session):
        autoload_with = connection.connection()
    else:
        autoload_with = connection

    return sa.Table(name,
                metadata,
                autoload=True,
                autoload_with=autoload_with,
                extend_existing=True,
                schema=schema)


def get_class(
    name: str,
    connection: SqlConnection,
    schema: Optional[str] = None
):
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
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    schema: str, default None
        Database schema name.
    
    Returns
    -------
    A SqlAlchemy table class object.
    """
    metadata = sa.MetaData(connection, schema=schema)
    if isinstance(connection, sa.orm.Session):
        reflect = connection.connection()
    else:
        reflect = connection

    metadata.reflect(reflect, only=[name], schema=schema)
    Base = automap_base(metadata=metadata)
    Base.prepare()
    return Base.classes[name]


def get_column(
    table: str,
    column_name: str
) -> sa.Column:
    return table.c[column_name]


def get_primary_key_constraints(
    table: sa.Table
) -> tuple[str, list[str]]:
    """
        Returns dictionary of primary key constraint names
        and list of column names per contraint.
    """
    cons = table.constraints
    for con in cons:
        if isinstance(con, PrimaryKeyConstraint):
            return con.name, [col.name for col in con.columns]


def get_column_types(table) -> dict[str, sa.sql.sqltypes]:
    """Returns dict of table column names:sql_type
    """
    return {c.name: c.type for c in table.c}


def get_column_names(table) -> list[str]:
    return [c.name for c in table.columns]


def get_row_count(table, session) -> int:
    col_name = get_column_names(table)[0]
    col = get_column(table, col_name)
    return session.execute(sa.func.count(col)).scalar()


def get_schemas(engine: Engine):
    insp = sa.inspect(engine)
    return insp.get_schema_names()