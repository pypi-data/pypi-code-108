from typing import Any, Optional, Union
from dataclasses import dataclass
from collections.abc import Iterable

from sqlalchemy.orm import Session
import sqlalchemy as sa

from sessionize.utils.delete import delete_records_session
from sessionize.utils.insert import insert_records_session
from sessionize.utils.update import update_records_session
from sessionize.utils.select import select_first_record, select_records, select_records_all
from sessionize.utils.sa_orm import get_table, has_primary_key, get_column_names
from sessionize.utils.sa_orm import get_column_types, get_row_count, primary_keys
from sessionize.utils.custom_types import Record, SqlConnection
from sessionize.exceptions import MissingPrimaryKey
from sessionize.orm.selection import Selection
from sessionize.orm.selection import TableSelection
from sessionize.exceptions import rollback_on_exception
from sessionize.orm.selection_chaining import selection_chaining
from sessionize.orm.session_parent import SessionParent


@selection_chaining
class SessionTable(SessionParent):
    def __init__(self, name: str, engine: sa.engine.Engine, schema: Optional[str] = None):
        SessionParent.__init__(self, engine)
        self.name = name
        self.schema = schema
        self.sa_table = get_table(self.name, self.session, self.schema)
        if not has_primary_key(self.sa_table):
            raise MissingPrimaryKey(
            'Sessionize requires sql table to have a primary key to work properly.\n' +
            'Use sessionize.create_primary_key to add a primary key to your table.')
        # Used when SessionTable is selected (__getitem__, __setitem__, __delitem__)
        self.table_selection = TableSelection(self, self.name, schema=self.schema)

    def __repr__(self) -> str:
        return repr_session_table(self.sa_table, self.session)

    def __iter__(self):
        return iter(self.table_selection)

    def __getitem__(self, key) -> Selection:
        return self.table_selection[key]
    
    def __setitem__(self, key, value) -> None:
        self.table_selection[key] = value

    def __delitem__(self, key):
        del self.table_selection[key]

    def __len__(self):
        return get_row_count(self.sa_table, self.session)

    def __add__(self, value: Union[Record, list[Record]]):
        # insert a record or list of records into table
        if isinstance(value, dict):
            self.insert_one_record(value)
        elif isinstance(value, Iterable) and not isinstance(value, str):
            self.insert_records(value)
        else:
            raise TypeError('value must be a dictionary or list')
        return self

    def __iadd__(self, value: Union[Record, list[Record]]) -> None:
        return self.__add__(value)

    @property
    def columns(self):
        return get_column_names(self.sa_table)

    @property
    def records(self):
        return select_records_all(self.sa_table, self.session)

    @property
    def primary_keys(self):
        return primary_keys(self.sa_table)

    def info(self):
        return select_table_info(self.sa_table, self.session)

    def insert_records(self, records: list[Record]) -> None:
        insert_records_session(self.sa_table, records, self.session, schema=self.schema)

    def insert_one_record(self, record: Record) -> None:
        self.insert_records([record])

    def update_records(self, records: list[Record]) -> None:
        update_records_session(self.sa_table, records, self.session, schema=self.schema)

    def update_one_record(self, record: Record) -> None:
        self.update_records([record])

    def delete_records(self, column_name: str, values: list[Any]) -> None:
        delete_records_session(self.sa_table, column_name, values, self.session, schema=self.schema)

    def delete_one_record(self, column_name: str, value: Any) -> None:
        self.delete_records(column_name, [value])

    def select_records(self, chunksize=None) -> list[Record]:
        return select_records(self.sa_table, self.session, chunksize=chunksize, schema=self.schema)

    def head(self, size=5):
        return self[:size]

    def tail(self, size=5):
        return self[-size:]


@dataclass
class TableInfo():
    name: str
    types: dict[str, sa.sql.sqltypes]
    row_count: int
    keys: list[str]
    first_record: Record
    schema: Optional[str] = None


def select_table_info(table: sa.Table, connection: SqlConnection) -> TableInfo:
    types = get_column_types(table)
    row_count = get_row_count(table, connection)
    keys = primary_keys(table)
    first_record = select_first_record(table, connection)
    return TableInfo(table.name, types, row_count, keys, first_record, table.schema)


def repr_session_table(
    table: sa.Table,
    connection: SqlConnection
) -> str:
    table_info = select_table_info(table, connection)
    types = table_info.types
    row_count = table_info.row_count
    keys = table_info.keys
    first_record = table_info.first_record
    name = table.name if table.schema is None else f"{table.name}', schema='{table.schema}"
    return f"""SessionTable(name='{name}', keys={keys}, row_count={row_count},
             first_record={first_record},
             sql_data_types={types})"""