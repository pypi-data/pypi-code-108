from typing import Optional, Union

from sessionize.sa_versions.sa_1_4_29.sa import SqlAlchemy, Record, Table, Engine, Session
from sessionize.utils.sa_orm import _get_table


def insert_from_table_session(
    sa_table1: Union[Table, str],
    sa_table2: Union[Table, str],
    session: Session,
    schema: Optional[str] = None,
) -> None:
    """
    Inserts all records from table1 into table2.
    Only add inserts to session. Does not execute.
    """
    table1 = _get_table(sa_table1, session, schema=schema)
    table2 = _get_table(sa_table2, session, schema=schema)
    SqlAlchemy.insert_from_table_session(table1, table2, session)


def insert_from_table(
    sa_table1: Union[Table, str],
    sa_table2: Union[Table, str],
    engine: Engine,
    schema: Optional[str] = None,
) -> None:
    """
    Inserts all records from table1 into table2.
    Executes inserts.
    """
    table1 = _get_table(sa_table1, engine, schema=schema)
    table2 = _get_table(sa_table2, engine, schema=schema)
    SqlAlchemy.insert_from_table(table1, table2, engine)


def insert_records_session(
    sa_table: Union[Table, str],
    records: list[Record],
    session: Session,
    schema: Optional[str] = None
) -> None:
    """
    Inserts list of records into sql table.
    Only adds sql records inserts to session, does not commit session.
    Sql table must have primary key.
    
    Parameters
    ----------
    sa_table: sa.Table
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
    table = _get_table(sa_table, session, schema=schema)
    SqlAlchemy.insert_records_session(table, records, session)


def insert_records(
    sa_table: Union[Table, str],
    records: list[Record],
    engine: Engine,
    schema: Optional[str] = None
) -> None:
    table = _get_table(sa_table, engine, schema=schema)
    SqlAlchemy.insert_records(table, records, engine)