from typing import Optional, Union

from sessionize.sa_versions.sa_1_4_29.sa import SqlAlchemy, Record, Engine, Table, Session
from sessionize.utils.sa_orm import _get_table


def update_records_session(
    table: Union[Table, str],
    records: list[Record],
    session: Session,
    schema: Optional[str] = None
) -> None:
    """
    Update sql table records from list records.
    Only adds sql records updates to session, does not commit session.
    Sql table must have primary key.
    Do not pass any records that do not already have primary key matches in table.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
        Use sessionize.engine_utils.get_table to get table.
    records: list[Record]
        list of records to update.
        Use df.to_dict('records') to convert Pandas DataFrame to records.
    session: sa.orm.session.Session
        SqlAlchemy session to add sql updates to.
    schema: str, default None
        Database schema name.
    table_class: DeclarativeMeta, default None
        pass in the table class if you already have it
        otherwise, will query sql for it each time.

    Returns
    -------
    None
    """
    table = _get_table(table, session, schema=schema)
    SqlAlchemy.update_records_session(table, records, session)


def update_records(
    sa_table: Union[Table, str],
    records: list[Record],
    engine: Engine,
    schema: Optional[str] = None
) -> None:
    table = _get_table(sa_table, engine, schema=schema)
    SqlAlchemy.update_records(table, records, engine)