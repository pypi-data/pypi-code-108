from collections.abc import Iterator

from sessionize.utils.select import select_record_by_index, select_record_by_primary_key, select_record_by_primary_key


class TableIterator(Iterator):
    def __init__(self, table_selection):
        self.i = 0
        self.table = table_selection

    def __next__(self):
        index = self.i
        if index < len(self.table):
            self.i += 1
            return select_record_by_index(self.table.sa_table, self.table.session, index)
        else:
            raise StopIteration


class SubTableIterator(Iterator):
    def __init__(self, subtable_selection):
        self.i = 0
        self.subtable = subtable_selection

    def __next__(self):
        index = self.i
        if index < len(self.subtable):
            self.i += 1
            return select_record_by_primary_key(self.subtable.sa_table,
                                                self.subtable.session,
                                                self.subtable.primary_key_values[index])
        else:
            raise StopIteration


class ColumnIterator(Iterator):
    def __init__(self, column_selection):
        self.i = 0
        self.column = column_selection

    def __next__(self):
        index = self.i
        if index < len(self.column):
            self.i += 1
            record = select_record_by_index(self.column.sa_table, self.column.session, index)
            return record[self.column.column_name]
        else:
            raise StopIteration

        
class SubColumnIterator(Iterator):
    def __init__(self, column_selection):
        self.i = 0
        self.column = column_selection

    def __next__(self):
        index = self.i
        if index < len(self.column):
            self.i += 1
            record = select_record_by_primary_key(self.column.sa_table,
                                                  self.column.session,
                                                  self.column.primary_key_values[index])
            return record[self.column.column_name]
        else:
            raise StopIteration