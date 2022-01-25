from typing import Optional, Union

from sessionize.sa_versions.sa_1_4_29.sa import SqlAlchemy, SqlConnection, Table, Engine, Column, Session, sql


def _get_table_name(
    table_name: Union[Table, str]
) -> str:
    if isinstance(table_name, Table):
        return table_name.name
    if isinstance(table_name, str):
        return table_name


def _get_table(
    sa_table: Union[str, Table],
    engine: Engine,
    schema: Optional[str] = None
) -> Table:
    if isinstance(sa_table, Table):
        return sa_table
    if isinstance(sa_table, str):
        return get_table(sa_table, engine, schema=schema)


def primary_keys(sa_table: Table) -> list[str]:
    """
    Given SqlAlchemy Table, query database for
    columns with primary key constraint.
    Returns a list of column names.
    
    Parameters
    ----------
    sa_table: sa.Table
        SqlAlchemy table mapped to sql table.
    
    Returns
    -------
    list of primary key names.
    """
    return SqlAlchemy.primary_key_names(sa_table)


def has_primary_key(sa_table: Table) -> bool:
    """
    Given a SqlAlchemy Table, query database to
    check for primary keys.
    Returns True if table has primary key,
    False if no primary key.
    
    Parameters
    ----------
    sa_table: sa.Table
        SqlAlchemy table mapped to sql table.
    
    Returns
    -------
    bool
    """
    return len(primary_keys(sa_table)) != 0


def get_table(
    table_name: str,
    connection: SqlConnection,
    schema: Optional[str] = None
) -> Table:
    """
    Maps a SqlAlchemy Table to a sql table.
    Returns SqlAlchemy Table object.
    
    Parameters
    ----------
    table_name: str
        name of sql table to map.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    schema: str, default None
        Database schema name.
    
    Returns
    -------
    A SqlAlchemy mapped Table object.
    """
    return SqlAlchemy.get_table(table_name, connection, schema)


def get_class(
    table_name: str,
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
    table_name: str
        name of sql table to map.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    schema: str, default None
        Database schema name.
    
    Returns
    -------
    A SqlAlchemy table class object.
    """
    return SqlAlchemy.get_class(table_name, connection, schema)


def get_column(
    sa_table: Table,
    column_name: str
) -> Column:
    return SqlAlchemy.get_column(sa_table, column_name)


def get_primary_key_constraints(
    sa_table: Table
) -> tuple[str, list[str]]:
    """
        Returns dictionary of primary key constraint names
        and list of column names per contraint.
    """
    return SqlAlchemy.get_primary_key_constraints(sa_table)


def get_column_types(sa_table: Table) -> dict[str, sql.sqltypes]:
    """Returns dict of table column names:sql_type
    """
    return SqlAlchemy.get_column_types(sa_table)


def get_column_names(sa_table: Table) -> list[str]:
    return SqlAlchemy.get_column_names(sa_table)


def get_row_count(sa_table: Table, session: Session) -> int:
    return SqlAlchemy.get_row_count(sa_table, session)


def get_schemas(engine: Engine):
    return SqlAlchemy.get_schemas(engine)