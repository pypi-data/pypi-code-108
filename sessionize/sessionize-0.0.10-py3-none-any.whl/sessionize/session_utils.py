from typing import Optional

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm.decl_api import DeclarativeMeta

from engine_utils import has_primary_key, get_class, get_column
from basic_utils import divide_chunks


def delete_rows_session(
    table: sa.Table,
    col_name: str,
    values: list,
    session: sa.orm.session.Session
) -> None:
    """
    Given a SqlAlchemy Table, name of column to compare,
    list of values to match, and SqlAlchemy session object,
    deletes sql rows where column values match given values.
    Only adds sql row deletions to session, does not commit session.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    col_name: str
        name of sql table column to compare to values.
    values: list
        list of values to match with column values.
    session: sa.orm.session.Session
        SqlAlchemy session to add sql deletes to.
    
    Returns
    -------
    None
    """
    col = table.c[col_name]
    session.query(table).filter(col.in_(values)).delete(synchronize_session=False)


def insert_df_session(
    table: sa.Table,
    df: pd.DataFrame,
    session: sa.orm.session.Session,
    chunk_size: int = 500,
    schema: Optional[str] = None,
    table_class: Optional[DeclarativeMeta] = None,
    has_key: Optional[bool] = None
) -> None:
    """
    Inserts sql rows from Pandas DataFrame into sql table.
    Only adds sql row inserts to session, does not commit session.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    df: pd.DataFrame
        Pandas DataFrame to add rows from.
    session: sa.orm.session.Session
        SqlAlchemy session to add sql inserts to.
    chunk_size: int, default 500
        size of chunks of rows to insert if not primary key
    schema: str, default None
        Database schema name.
    table_class: DeclarativeMeta, default None
        pass in the table class if you already have it
        otherwise, will query sql to query for it each time.
    has_key: bool, default None
        pass in if sql table has primary key or not
        otherwise, will query sql to check each time.
        
    Returns
    -------
    None
    """
    records = df.to_dict('records')
    engine = session.get_bind()
    table_name = table.name
    has_key = has_primary_key(table) if has_key is None else has_key
    if has_key:
        if table_class is None:
            table_class = get_class(table_name, engine, schema=schema)
        mapper = sa.inspect(table_class)
        session.bulk_insert_mappings(mapper, records)
    else:
        for chunk in divide_chunks(records, chunk_size):
            session.execute(table.insert().values(chunk))


def update_df_session(
    table: sa.Table,
    df: pd.DataFrame,
    session: sa.orm.session.Session,
    col_name: Optional[str] = None,
    schema: Optional[str] = None,
    table_class: Optional[DeclarativeMeta] = None,
    has_key: Optional[bool] = None
) -> None:
    """
    Update sql rows from Pandas DataFrame into sql table.
    Only adds sql row updates to session, does not commit session.
    For tables with primary keys, do not pass any records in df
    that do not already have primary key matches in table.
    For tables without primary keys, pass in col_name for column
    used to check which rows to update.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    df: pd.DataFrame
        Pandas DataFrame to update rows from.
    session: sa.orm.session.Session
        SqlAlchemy session to add sql updates to.
    col_name: str, default None
        if table has no primary key, need column name
        to use to check which rows to update
    schema: str, default None
        Database schema name.
    table_class: DeclarativeMeta, default None
        pass in the table class if you already have it
        otherwise, will query sql to query for it each time.
    has_key: bool, default None
        pass in if sql table has primary key or not
        otherwise, will query sql to check each time.
    Returns
    -------
    None
    """
    records = df.to_dict('records')
    engine = session.get_bind()
    table_name = table.name
    has_key = has_primary_key(table) if has_key is None else has_key
    if has_key:
        if table_class is None:
            table_class = get_class(table_name, engine, schema=schema)
        mapper = sa.inspect(table_class)
        session.bulk_update_mappings(mapper, records)
    else:
        if col_name is None:
            raise ValueError('col_name must be specified for table without primary key.')
        column = get_column(table, col_name)
        for record in records:
            session.query(table).where(column.in_([record[col_name]])).update(record)