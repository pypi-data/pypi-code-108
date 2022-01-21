from typing import Optional, Union

import sqlalchemy as sa
from sqlalchemy.orm import Session

from sessionize.utils.custom_types import Record
from sessionize.utils.sa_orm import _get_table

# TODO: finish insert_update_records_session function
def insert_update_records_session(
    table: Union[sa.Table, str],
    records: list[Record],
    session: Session,
    schema: Optional[str] = None
) -> None:
    """
    Insert new records and update existing records in sql table.
    Only adds sql records updates and inserts to session, does not commit session.
    Sql table must have primary key.
    Uses primary key values to determine if records are updates or inserts.
    If record has no primary key value, will try to insert.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
        Use sessionize.engine_utils.get_table to get table.
    records: list[Record]
        list of records to update or insert.
        Use df.to_dict('records') to convert Pandas DataFrame to records.
    session: sa.orm.session.Session
        SqlAlchemy session to add sql updates and inserts to.
    schema: str, default None
        Database schema name.

    Returns
    -------
    None
    """
    table = _get_table(table, session)
    # figure out which records are updates, with primary key matches
    updates = []

    # insert the rest of the records
    inserts = []

