from collections.abc import Iterable, Iterator
from typing import Optional
from numbers import Number

from sessionize.utils.custom_types import Record

from sessionize.utils.select import select_primary_key_record_by_index
from sessionize.utils.select import select_primary_key_records_by_slice
from sessionize.utils.select import select_records_by_primary_keys
from sessionize.utils.select import select_record_by_primary_key
from sessionize.utils.select import select_records_by_primary_keys
from sessionize.utils.select import select_column_values_all
from sessionize.utils.select import select_column_values_by_primary_keys
from sessionize.utils.select import select_primary_key_values
from sessionize.utils.select import select_value_by_primary_keys
from sessionize.utils.select import select_records
from sessionize.utils.select import select_record_by_index

from sessionize.utils.update import update_records_session

from sessionize.utils.insert import insert_records_session

from sessionize.utils.delete import delete_records_by_values_session
from sessionize.utils.delete import delete_record_by_values_session

from sessionize.orm.filter import Filter
from sessionize.orm.selection_chaining import selection_chaining
from sessionize.utils.sa_orm import get_table, get_row_count

from sessionize.orm.iterators import TableIterator, SubTableIterator, ColumnIterator, SubColumnIterator
from sessionize.orm.session_parent import SessionParent



class Selection:
    def __init__(self, parent: SessionParent, table_name: str, schema: Optional[str] = None):
        self.parent = parent
        self.session = parent.session
        self.table_name = table_name
        self.schema = schema
        self.sa_table = get_table(table_name, self.session, schema=schema)


@selection_chaining
class TableSelection(Selection):
    def __init__(self, parent: SessionParent, table_name: str, schema: Optional[str] = None):
        Selection.__init__(self, parent, table_name, schema=schema)

    def __repr__(self):
        if len(self) == 0:
            first_record = None
        else:
            first_record = select_record_by_index(self.sa_table, self.session, 0)
        if self.schema is None:
            return f"TableSelection(name='{self.table_name}', first_record={first_record})"
        return f"TableSelection(name='{self.table_name}', first_record={first_record}, schema='{self.schema}')"

    def __iter__(self):
        return TableIterator(self)

    def __len__(self):
        return get_row_count(self.sa_table, self.session)

    def __add__(self, other):
        if isinstance(other, Iterable) and not isinstance(other, dict):
            self.insert(other)
        else:
            self.insert([other])

    def __getitem__(self, key):
        if isinstance(key, int):
            # TableSelection[index] -> RecordSelection
            primary_key_values = self.get_primary_key_values()
            return RecordSelection(self.parent, primary_key_values[key], self.table_name)

        if isinstance(key, slice):
            # TableSelection[slice] -> SubTableSelection
            _slice = key
            primary_key_values = self.get_primary_key_values()
            if _slice.start is None and _slice.stop is None:
                # TableSelection[:] -> TableSelection
                return TableSelection(self.parent)
            return SubTableSelection(self.parent, primary_key_values[_slice], self.table_name)

        if isinstance(key, str):
            # TableSelection[column_name] -> ColumnSelection
            column_name = key
            return ColumnSelection(self.parent, column_name, self.table_name)

        # if isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')
            
        if isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # TableSelection[filter] -> SubTableSelection
            filter = key
            primary_keys = self.get_primary_keys_by_filter(filter)
            return SubTableSelection(self.parent, primary_keys, self.table_name)

        if isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # TableSelection[column_names] -> TableSubColumnSelection
            column_names = key
            return TableSubColumnSelection(self.parent, column_names, self.table_name)

        raise NotImplemented('TableSelection only supports selection by int, slice, str, Iterable[bool], and Iterable[str]')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            # TableSelection[index] = value
            index = key
            record_selection = self[index]
            record_selection.update(value)

        elif isinstance(key, slice):
            # TableSelection[slice] = value
            _slice = key
            sub_table_selection = self[_slice]
            sub_table_selection.update(value)

        elif isinstance(key, str):
            # TableSelection[column_name] = value
            column_name = key
            column_selection = self[column_name]
            column_selection.update(value)

        # elif isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # TableSelection[Iterable[bool]] = value
            filter = key
            sub_table_selection = self[filter]
            sub_table_selection.update(value)

        elif isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # TableSelection[column_names] = value
            raise NotImplemented('TableSubColumnSelection updating is not implemented.')

        else:
            raise NotImplemented('TableSelection only supports selection updating by int, slice, str, and Iterable[bool]')

    def __delitem__(self, key):
        if isinstance(key, int):
            # del TableSelection[index]
            index = key
            record_selection = self[index]
            record_selection.delete()

        elif isinstance(key, slice):
            # del TableSelection[slice]
            _slice = key
            sub_table_selection = self[_slice]
            sub_table_selection.delete()

        elif isinstance(key, str):
            # del TableSelection[column_name]
            column_selection = self[key]
            column_selection.delete()

        # elif isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # del TableSelection[filter]
            filter = key
            sub_table_selection = self[filter]
            sub_table_selection.delete()

        elif isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # del TableSelection[column_names]
            raise NotImplemented('TableSubColumnSelection deletion is not implemented.')
        else:
            raise NotImplemented('TableSelection only supports selection deletion by int, slice, str, and, Iterable[bool]')

    @property
    def records(self) -> list:
        return select_records(self.sa_table, self.session)

    def head(self, size=5):
        if size < 0:
            raise ValueError('size must be a positive number')
        return self[:size]

    def tail(self, size=5):
        if size < 0:
            raise ValueError('size must be a positive number')
        return self[-size:]

    def get_primary_keys_by_index(self, index: int) -> Record:
        return select_primary_key_record_by_index(self.sa_table, self.session, index)

    def get_primary_keys_by_slice(self, _slice: slice) -> list[Record]:
        return select_primary_key_records_by_slice(self.sa_table, self.session, _slice)

    # TODO: select_primary_key_values_by_filter function
    def get_primary_keys_by_filter(self, filter: Iterable[bool]) -> list[Record]:
        primary_key_values = self.get_primary_key_values()
        return [record for record, b in zip(primary_key_values, filter) if b]

    def get_primary_key_values(self) -> list[Record]:
        return select_primary_key_values(self.sa_table, self.session)

    def update(self, records: list[Record]) -> None:
        # TODO: check if records match primary key values
        update_records_session(self.sa_table, records, self.session)

    def insert(self, records: list[Record]) -> None:
        # TODO: check if records don't match any primary key values
        insert_records_session(self.sa_table, records, self.session)

    def delete(self) -> None:
        # delete all records in sub table
        delete_records_by_values_session(self.sa_table, self.primary_key_values, self.session)


@selection_chaining
class TableSubColumnSelection(TableSelection):
    # returned when all records are selected but a subset of columns are selected
    def __init__(self, parent: SessionParent, column_names: Iterable[str], table_name: str):
        TableSelection.__init__(self, parent, table_name)
        self.column_names = column_names

    def __repr__(self):
        return f"TableSubColumnSelection(name='{self.table_name}', records={self.records})"

    @property
    def records(self) -> list[Record]:
        return select_records(self.sa_table, self.session, include_columns=self.column_names)

    def __getitem__(self, key):
        if isinstance(key, int):
            # TableSubColumnSelection[index] -> SubRecordSelection
            index = key
            primary_key_values = self.get_primary_key_values()
            return SubRecordSelection(self.parent, primary_key_values[index], self.column_names)

        if isinstance(key, slice):
            # TableSubColumnSelection[slice] -> SubTableSubColumnSelection
            _slice = key
            primary_key_values = self.get_primary_key_values()
            return SubTableSubColumnSelection(self.parent, primary_key_values[_slice], self.column_names, self.table_name)

        if isinstance(key, str):
            # TableSubColumnSelection[column_name] -> ColumnSelection
            column_name = key
            return ColumnSelection(self.parent, column_name, self.table_name)

        # if isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        if isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # TableSubColumnSelection[filter]
            filter = key
            primary_keys = self.get_primary_keys_by_filter(filter)
            return SubTableSubColumnSelection(self.parent, primary_keys, self.column_names, self.table_name)

        if isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # TableSubColumnSelection[column_names]
            column_names = key
            return TableSubColumnSelection(self.parent, column_names, self.table_name)

        raise NotImplemented('TableSubColumnSelection only supports selection by int, slice, str, Iterable[bool], and Iterable[str].')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            # TableSubColumnSelection[index] = value
            index = key
            sub_record_selection = self[index]
            sub_record_selection.update(value)

        elif isinstance(key, slice):
            # TableSubColumnSelection[slice] = value
            _slice = key
            sub_table_sub_column_selection = self[_slice]
            sub_table_sub_column_selection.update(value)

        elif isinstance(key, str):
            # TableSubColumnSelection[column_name] = value
            column_name = key
            sub_column_selection = self[column_name]
            sub_column_selection.update(value)

        # elif isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # TableSubColumnSelection[Iterable[bool]] = value
            raise NotImplemented('SubTableSubColumnSelection updating is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # TableSubColumnSelection[column_names] = value
            raise NotImplemented('TableSubColumnSelection updating is not implemented.')

        else:
            raise NotImplemented('TableSubColumnSelection only supports selection updating by int, slice, and str.')

    def __delitem__(self, key):
        if isinstance(key, int):
            # del TableSubColumnSelection[index]
            raise NotImplemented('SubRecordSelection deletion is not implemented.')

        if isinstance(key, slice):
            # del TableSubColumnSelection[slice]
            raise NotImplemented('SubTableSubColumnSelection deletion is not implemented.')

        if isinstance(key, str):
            # del TableSubColumnSelection[column_name]
            raise NotImplemented('SubColumnSelection deletion is not implemented.')

        # if isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        if isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # del TableSubColumnSelection[filter]
            raise NotImplemented('SubTableSubColumnSelection deletion is not implemented.')

        if isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # del TableSubColumnSelection[column_names]
            raise NotImplemented('TableSubColumnSelection deletion is not implemented.')

        raise NotImplemented('TableSubColumnSelection does not support deletion.')
     
@selection_chaining
class SubTableSelection(TableSelection):
    # returned when a subset of records is selecected
    def __init__(self, parent: SessionParent, primary_key_values: list[Record], table_name: str):
        TableSelection.__init__(self, parent, table_name)
        self.primary_key_values = primary_key_values

    def __repr__(self):
        return f"SubTableSelection(name='{self.table_name}', records={self.records})"

    def __iter__(self):
        return SubTableIterator(self)

    def __len__(self):
        return len(self.primary_key_values)

    def __getitem__(self, key):
        if isinstance(key, int):
            # SubTableSelection[index] -> RecordSelection
            primary_key_values = self.get_primary_key_values()
            return RecordSelection(self.parent, primary_key_values[key])

        if isinstance(key, slice):
            # SubTableSelection[slice] -> SubTableSelection
            _slice = key
            primary_key_values = self.get_primary_key_values()
            return SubTableSelection(self.parent, primary_key_values[_slice])

        if isinstance(key, str):
            # SubTableSelection[column_name] -> SubColumnSelection
            column_name = key
            primary_key_values = self.get_primary_key_values()
            return SubColumnSelection(self.parent, column_name, primary_key_values)

        # if isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        if isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # SubTableSelection[filter] -> SubTableSelection
            filter = key
            primary_keys = self.get_primary_keys_by_filter(filter)
            return SubTableSelection(self.parent, primary_keys)

        if isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # SubTableSelection[column_names] -> SubTableSubColumnSelection
            column_names = key
            return SubTableSubColumnSelection(self.parent, column_names, column_names)

        raise NotImplemented('SubTableSelection only supports selection by int, slice, str, Iterable[bool], and Iterable[str].')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            # SubTableSelection[index] = value
            index = key
            sub_record_selection = self[index]
            sub_record_selection.update(value)

        elif isinstance(key, slice):
            # SubTableSelection[slice] = value
            _slice = key
            sub_table_selection = self[_slice]
            sub_table_selection.update(value)

        elif isinstance(key, str):
            # SubTableSelection[column_name] = value
            column_name = key
            sub_column_selection = self[column_name]
            sub_column_selection.update(value)

        # elif isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # SubTableSelection[Iterable[bool]] = value
            raise NotImplemented('SubTableSubColumnSelection updating is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # SubTableSelection[column_names] = value
            raise NotImplemented('SubTableSubColumnSelection updating is not implemented.')

        else:
            raise NotImplemented('SubTableSelection only supports selection updating by int, slice, and str.')

    def __delitem__(self, key):
        # del SubTableSelection[key]
        if isinstance(key, int):
            # del SubTableSelection[index]
            index = key
            sub_record_selection = self[index]
            sub_record_selection.delete()

        elif isinstance(key, slice):
            # del SubTableSelection[slice]
            _slice = key
            sub_table_selection = self[_slice]
            sub_table_selection.delete()

        elif isinstance(key, str):
            # del SubTableSelection[column_name]
            raise NotImplemented('SubColumnSelection deletion is not implemented.')

        # elif isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # del SubTableSelection[filter]
            raise NotImplemented('SubTableSubColumnSelection deletion is not implemented.')

        elif isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # del SubTableSelection[column_names]
            raise NotImplemented('TableSubColumnSelection deletion is not implemented.')

        else:
            raise NotImplemented('SubTableSelection only supports selection updating by int and slice.')

    @property
    def records(self) -> list[Record]:
        return select_records_by_primary_keys(self.sa_table, self.session, self.primary_key_values)

    def get_primary_key_values(self):
        return self.primary_key_values

    def get_primary_keys_by_index(self, index: int):
        return self.primary_key_values[index]

    def get_primary_keys_by_slice(self, _slice: slice):
        return self.primary_key_values[_slice]

    def get_primary_keys_by_filter(self, filter: Iterable[bool]):
        return [record for record, b in zip(self.primary_key_values, filter) if b]

@selection_chaining
class SubTableSubColumnSelection(SubTableSelection):
    # returned when a subset of records is selected and a subset of columns is selected
    def __init__(
        self,
        parent: SessionParent,
        primary_key_values: list[Record],
        column_names: list[str],
        table_name: str
    ) -> None:
        SubTableSelection.__init__(self, parent, primary_key_values, table_name)
        self.column_names = column_names

    def __repr__(self):
            return f"SubTableSubColumnSelection(name='{self.table_name}', records={self.records})" 

    def __getitem__(self, key):
        if isinstance(key, int):
            # SubTableSubColumnSelection[index] -> SubRecordSelection
            primary_key_values = self.get_primary_key_values()
            return SubRecordSelection(self.parent, primary_key_values[key], self.column_names)

        if isinstance(key, slice):
            # SubTableSubColumnSelection[slice] -> SubTableSubColumnSelection
            _slice = key
            primary_key_values = self.get_primary_key_values()
            return SubTableSubColumnSelection(self.parent, primary_key_values[_slice], self.column_names, self.table_name)

        if isinstance(key, str):
            # SubTableSubColumnSelection[column_name] -> SubColumnSelection
            column_name = key
            primary_key_values = self.get_primary_key_values()
            _type = type(self)
            return SubColumnSelection(self.parent, column_name, primary_key_values, self.table_name)

        # if isinstance(key, tuple):
        #     raise NotImplemented('tuple selection is not implemented.')

        if isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # SubTableSubColumnSelection[filter] -> SubTableSubColumnSelection
            filter = key
            primary_keys = self.get_primary_keys_by_filter(filter)
            return SubTableSubColumnSelection(self.parent, primary_keys, self.column_names, self.table_name)

        if isinstance(key, Iterable) and all(isinstance(item, str) for item in key):
            # SubTableSubColumnSelection[column_names] -> SubTableSubColumnSelection
            column_names = key
            return SubTableSubColumnSelection(self.parent, column_names, column_names, self.table_name)

        raise NotImplemented('SubTableSubColumnSelection only supports selection by int, slice, str, Iterable[bool], and Iterable[str].')

    @property
    def records(self):
        return select_records_by_primary_keys(self.sa_table,
                                              self.session,
                                              self.primary_key_values,
                                              include_columns=self.column_names)

@selection_chaining
class ColumnSelection(Selection):
    # returned when a column is selected
    def __init__(self, parent: SessionParent, column_name: str, table_name: str):
        Selection.__init__(self, parent, table_name)
        self.column_name = column_name

    def __repr__(self):
        return f"""ColumnSelection(table_name='{self.table_name}', column_name='{self.column_name}', values={self.values})"""

    def __iter__(self):
        return ColumnIterator(self)

    def __len__(self):
        return len(self.parent)

    def __getitem__(self, key):
        if isinstance(key, int):
            # ColumnSelection[int]
            index = key
            primary_key_values = self.get_primary_key_values()
            return ValueSelection(self.parent, self.column_name, primary_key_values[index])
        
        if isinstance(key, slice):
            # ColumnSelection[slice]
            _slice = key
            primary_key_values = self.get_primary_key_values()
            return SubColumnSelection(self.parent, self.column_name, primary_key_values[_slice])

        if isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # ColumnSelection[Iterable[bool]]
            filter = key
            primary_key_values = self.get_primary_keys_by_filter(filter)
            return SubColumnSelection(self.parent, self.column_name, primary_key_values)

        raise NotImplemented('ColumnSelection only supports selection by int, slice, and Iterable[bool].')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            # ColumnSelection[int] = value
            index = key
            value_selection = self[index]
            value_selection.update(value)
        
        elif isinstance(key, slice):
            # ColumnSelection[slice] = value
            _slice = key
            sub_column_selection = self[_slice]
            sub_column_selection.update(value)

        elif isinstance(key, Iterable) and all(isinstance(item, bool) for item in key):
            # ColumnSelection[Iterable[bool]] = value
            filter = key
            sub_column_selection = self[filter]
            sub_column_selection.update(value)

        else:
            raise NotImplemented('ColumnSelection only supports selection updating by int, slice, and Iterable[bool].')

    def __add__(self, value) -> None:
        # update values by adding value
        records = self.get_records()
        if isinstance(value, Number):
            for record in records:
                record[self.column_name] += value

        elif isinstance(value, Iterable) and not isinstance(value, str):
            for record, val in zip(records, value):
                record[self.column_name] += val

        update_records_session(self.sa_table, records, self.session)

    def __sub__(self, value) -> None:
        # update values by subtracting value
        records = self.get_records()
        if isinstance(value, Number):
            for record in records:
                record[self.column_name] -= value

        elif isinstance(value, Iterable) and not isinstance(value, str):
            for record, val in zip(records, value):
                record[self.column_name] -= val

        update_records_session(self.sa_table, records, self.session)

    def __eq__(self, other) -> Filter:
        # ColumnSelection == value
        # Returns filter
        if isinstance(other, Iterable) and not isinstance(other, str):
            return Filter([value == item for value, item in zip(self.values, other)])

        return Filter([item == other for item in self.values])

    def __ne__(self, other) -> Filter:
        # ColumnSelection != value
        # Return filter
        if isinstance(other, Iterable) and not isinstance(other, str):
            return Filter([value != item for value, item in zip(self.values, other)])

        return Filter([item != other for item in self.values])

    def __ge__(self, other) -> Filter:
        # ColumnSelection >= value
        # Return filter
        if isinstance(other, Iterable) and not isinstance(other, str):
            return Filter([value >= item for value, item in zip(self.values, other)])

        return Filter([value >= other for value in self.values])

    def __le__(self, other) -> Filter:
        # ColumnSelection <= value
        # Return filter
        if isinstance(other, Iterable) and not isinstance(other, str):
            return Filter([value <= item for value, item in zip(self.values, other)])

        return Filter([value <= other for value in self.values])

    def __lt__(self, other) -> Filter:
        # ColumnSelection < value
        # Return filter
        if isinstance(other, Iterable) and not isinstance(other, str):
            return Filter([value < item for value, item in zip(self.values, other)])

        return Filter([item < other for item in self.values])

    def __gt__(self, other) -> Filter:
        # ColumnSelection > value
        # Return filter
        if isinstance(other, Iterable) and not isinstance(other, str):
            return Filter([value > item for value, item in zip(self.values, other)])

        return Filter([item > other for item in self.values])

    @property
    def values(self):
        return select_column_values_all(self.sa_table, self.session, self.column_name)

    def get_records(self):
        return select_records(self.sa_table, self.session)

    def get_primary_key_values(self):
        return select_primary_key_values(self.sa_table, self.session)

    def get_primary_keys_by_filter(self, filter: Iterable[bool]):
        primary_key_values = self.get_primary_key_values()
        return [record for record, b in zip(primary_key_values, filter) if b]

    def get_primary_keys_by_index(self, index):
        primary_keys = self.get_primary_key_values()
        return primary_keys[index]

    def get_primary_keys_by_slice(self, _slice):
        primary_keys = self.get_primary_key_values()
        return primary_keys[_slice]

    def get_primary_keys_by_filter(self, filter: Iterable[bool]):
        primary_key_values = self.get_primary_key_values()
        return [record for record, b in zip(primary_key_values, filter) if b]

    def update(self, values):
        primary_key_values = self.get_primary_key_values()
        if isinstance(values, Iterable) and not isinstance(values, str):
            for record, value in zip(primary_key_values, values):
                record[self.column_name] = value

        else:
            for record in primary_key_values:
                record[self.column_name] = values

        update_records_session(self.sa_table, primary_key_values, self.session)

@selection_chaining
class SubColumnSelection(ColumnSelection):
    # returned when a subset of a column is selecected
    def __init__(self, parent: SessionParent, column_name: str, primary_key_values: list[Record], table_name: str):
        ColumnSelection.__init__(self, parent, column_name, table_name)
        self.primary_key_values = primary_key_values

    def __repr__(self):
        return f"SubColumnSelection(table_name='{self.table_name}', column_name='{self.column_name}', values={self.values})"

    def __iter__(self):
        return SubColumnIterator(self)

    def __len__(self):
        return len(self.primary_key_values)

    @property
    def values(self):
        return select_column_values_by_primary_keys(self.sa_table, self.session, self.column_name, self.primary_key_values)

    def get_primary_key_values(self):
        return self.primary_key_values

    def get_records(self):
        return select_records_by_primary_keys(self.sa_table, self.session, self.primary_key_values)

@selection_chaining
class RecordSelection(Selection):
    # returned when a single record is selected with SessionTable
    def __init__(self, parent: SessionParent, primary_key_values: Record, table_name: str):
        Selection.__init__(self, parent, table_name)
        self.primary_key_values = primary_key_values

    def __repr__(self):
        return f"RecordSelection(table_name='{self.table_name}', record={self.record})"

    def __getitem__(self, key):
        column_name = key
        return ValueSelection(self.parent, column_name, self.primary_key_values, self.table_name)

    def __setitem__(self, key, value):
        column_name = key
        value_selection = self[column_name]
        value_selection.update(value)

    @property
    def record(self):
        records = select_record_by_primary_key(self.sa_table, self.session, self.primary_key_values)
        if len(records) == 0:
            raise KeyError('Primary key values do not exist in table.')
        else:
            return records[0]

    def update(self, record: Record) -> None:
        # update record with new values
        update_records_session(self.sa_table, [record], self.session)

    def delete(self) -> None:
        # delete the record
        delete_record_by_values_session(self.sa_table, self.primary_key_values, self.session)


class SubRecordSelection(Record):
    # returned when a record is selected and a subset of columns is selected
    def __init__(self, parent: SessionParent, primary_key_values: Record, column_names: list[str], table_name: str):
        RecordSelection.__init__(self, parent, primary_key_values, table_name)
        self.column_names = column_names

    def __repr__(self):
        return f"SubRecordSelection(table_name='{self.table_name}', subrecord={self.subrecord})"

    @property
    def subrecord(self):
        return select_records_by_primary_keys(self.sa_table,
                                              self.session,
                                              [self.primary_key_values],
                                              include_columns=self.column_names)[0]

            
class ValueSelection(Selection):
    # returned when a single value in a column is selecected
    def __init__(self, parent: SessionParent, column_name: str, primary_key_values: Record, table_name: str):
        Selection.__init__(self, parent, table_name)
        self.column_name = column_name
        self.primary_key_values = primary_key_values

    def __repr__(self):
        return f"ValueSelection(table_name='{self.table_name}', column_name='{self.column_name}', primary_key_values={self.primary_key_values}, value={self.value})"

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __lt__(self, other):
        return self.value < other

    def __sub__(self, value):
        # update value subtracting value
        record = self.primary_key_values.copy()
        record[self.column_name] = value - self.value
        update_records_session(self.sa_table, [record], self.session)

    def __add__(self, value):
        # update value adding value
        record = self.primary_key_values.copy()
        record[self.column_name] = value + self.value
        update_records_session(self.sa_table, [record], self.session)

    @property
    def value(self):
        return select_value_by_primary_keys(self.sa_table, self.session, self.column_name, self.primary_key_values)

    def update(self, value):
        # update the value in the table.
        record = self.primary_key_values.copy()
        record[self.column_name] = value
        update_records_session(self.sa_table, [record], self.session)