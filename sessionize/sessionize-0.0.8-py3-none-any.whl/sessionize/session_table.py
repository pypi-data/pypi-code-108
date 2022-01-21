from typing import Any, Optional

from sqlalchemy.orm import Session
import sqlalchemy as sa

from sessionize.utils.delete import delete_records_session
from sessionize.utils.insert import insert_records_session
from sessionize.utils.update import update_records_session
from sessionize.utils.sa_orm import get_table, has_primary_key
from sessionize.utils.custom_types import Record
from sessionize.exceptions import MissingPrimaryKey


class SessionTable:
    def __init__(self, name: str, engine: sa.engine.Engine, schema: Optional[str] = None):
        self.name = name
        self.engine = engine
        self.schema = schema
        self.session = Session(engine)
        # check for primary key column
        if not has_primary_key(self.get_sa_table()):
            raise MissingPrimaryKey('''sessionize requires sql table to have primary key to work properly.
            Use sessionize.create_primary_key to add a primary key to your table.''')

    def get_sa_table(self):
        return get_table(self.name, self.engine, self.schema)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.session.rollback()
        else:
            self.commit()

    def commit(self):
        self.session.commit()

    def insert_records(self, records: list[Record]) -> None:
        insert_records_session(self.get_sa_table(), records, self.session, schema=self.schema)

    def insert_one_record(self, record: Record) -> None:
        self.insert_records([record])

    def update_records(self, records: list[Record]) -> None:
        update_records_session(self.get_sa_table(), records, self.session, schema=self.schema)

    def update_one_record(self, record: Record) -> None:
        self.update_records([record])

    def delete_records(self, column_name: str, values: list[Any]) -> None:
        delete_records_session(self.get_sa_table(), column_name, values, self.session, schema=self.schema)

    def delete_one_record(self, column_name: str, value: Any) -> None:
        self.delete_records(column_name, [value])
