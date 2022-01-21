from typing import Optional, Union

import sqlalchemy as sa
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import PendingRollbackError

from sessionize.utils.custom_types import Record
from sessionize.utils.sa_orm import get_class, _get_table


def insert_from_table_session(
    table1: Union[sa.Table, str],
    table2: Union[sa.Table, str],
    session: sa.orm.Session,
    schema: Optional[str] = None,
) -> None:
    """
    Inserts all records from table1 into table2.
    Only add inserts to session. Does not execute.
    """
    table1 = _get_table(table1, session, schema=schema)
    table2 = _get_table(table2, session, schema=schema)
    session.execute(table2.insert().from_select(table1.columns.keys(), table1))


def insert_from_table(
    table1: Union[sa.Table, str],
    table2: Union[sa.Table, str],
    engine: sa.engine.Engine,
    schema: Optional[str] = None,
) -> None:
    """
    Inserts all records from table1 into table2.
    Executes inserts.
    """
    table1 = _get_table(table1, engine, schema=schema)
    table2 = _get_table(table2, engine, schema=schema)
    with sessionmaker(engine).begin() as session:
        insert_from_table_session(table1, table2, session)


def insert_records_session(
    table: Union[sa.Table, str],
    records: list[Record],
    session: sa.orm.Session,
    schema: Optional[str] = None
) -> None:
    """
    Inserts list of records into sql table.
    Only adds sql records inserts to session, does not commit session.
    Sql table must have primary key.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy Table mapped to sql table.
        Use sessionize.engine_utils.get_table to get table.
    records: list[Record]
        list of records to insert.
        Use df.to_dict('records') to convert Pandas DataFrame to records.
    session: sa.orm.session.Session
        SqlAlchemy session to add sql inserts to.
    schema: str, default None
        Database schema name.
    table_class: DeclarativeMeta, default None
        pass in the table class if you already have it
        otherwise, will query sql for it each time.
        
    Returns
    -------
    None
    """
    engine = session.get_bind()
    table = _get_table(table, engine, schema=schema)
    table_name = table.name
    table_class = get_class(table_name, engine, schema=schema)
    mapper = sa.inspect(table_class)
    session.bulk_insert_mappings(mapper, records)


def insert_records(
    table: Union[sa.Table, str],
    records: list[Record],
    engine: sa.engine.Engine,
    schema: Optional[str] = None
) -> None:
    table = _get_table(table, engine, schema=schema)
    with sessionmaker(engine).begin() as session:
        insert_records_session(table, records, session, schema)