from typing import Union, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import and_, or_
from sqlalchemy.exc import PendingRollbackError

from sessionize.utils.sa_orm import _get_table
from sessionize.utils.custom_types import Record


def delete_records_session(
    table: Union[sa.Table, str],
    col_name: str,
    values: list,
    session: Session,
    schema: Optional[str] = None
) -> None:
    """
    Given a SqlAlchemy Table, name of column to compare,
    list of values to match, and SqlAlchemy session object,
    deletes sql records where column values match given values.
    Only adds sql records deletions to session, does not commit session.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
        Use sessionize.engine_utils.get_table to get table.
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
    table = _get_table(table, session, schema=schema)
    col = table.c[col_name]
    session.query(table).filter(col.in_(values)).delete(synchronize_session=False)


def delete_record_by_values_session(
    table: Union[sa.Table, str],
    record: Record,
    session: Session,
    schema: Optional[str] = None
) -> None:
    # Delete any records that match the given record values.
    table = _get_table(table, session, schema=schema)
    where_clause = [table.c[key_name]==key_value for key_name, key_value in record.items()]
    if len(where_clause) == 0:
        return
    session.query(table).where((and_(*where_clause))).delete(synchronize_session=False)


def delete_records_by_values_session(
    table: Union[sa.Table, str],
    records: list[Record],
    session: Session,
    schema: Optional[str] = None
) -> None:
    # Delete any records that match the given records values.
    table = _get_table(table, session, schema=schema)
    where_clauses = []
    for record in records:
        where_clause = [table.c[key_name]==key_value for key_name, key_value in record.items()]
        where_clauses.append(and_(*where_clause))
    if len(where_clauses) == 0:
        return
    session.query(table).where((or_(*where_clauses))).delete(synchronize_session=False)


def delete_records(
    table: Union[sa.Table, str],
    col_name: str,
    values: list,
    engine: Engine,
    schema: Optional[str] = None
) -> None:
    with Session(engine) as session, session.begin():
        delete_records_session(table, col_name, values, session, schema=schema)


def delete_all_records_session(
    table: Union[sa.Table, str],
    session: Session,
    schema: Optional[str] = None
) -> None:
    table = _get_table(table, session, schema=schema)
    session.query(table).delete()


def delete_all_records(
    table: Union[sa.Table, str],
    engine: Engine,
    schema: Optional[str] = None
) -> None:
    with Session(engine) as session, session.begin():
        delete_all_records_session(table, session, schema=schema)
