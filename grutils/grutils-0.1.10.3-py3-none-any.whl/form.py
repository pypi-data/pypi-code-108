#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List

from .error import Error
from .formatter_and_parser import strip_if_str
from .iterable import first_match


class Row:
    def __init__(self, row_num=-1, cells: List[any] = None, do_strip=True):
        if cells is None:
            cells = []
        self.row_num = row_num
        if do_strip:
            self.cells = list(map(lambda x: strip_if_str(x), cells))
        else:
            self.cells = cells

    def __repr__(self):
        return '\nRow<row_num: {}, cells: {}>' \
            .format(self.row_num, self.cells)

    def __str__(self):
        return self.__repr__()

    def is_inited(self):
        return (self.row_num >= 0) and (self.cells is not None)

    def index(self, cell, err=None):
        i = first_match(lambda x: x == cell, self.cells).index
        if err is not None and i < 0:
            err.append('can not find cell ({})'.format(cell))
        return i

    def cell(self, column_index: int, err: Error):
        if not self.is_inited():
            err.append('row is not inited')
            return None
        if column_index >= len(self.cells) or column_index < 0:
            err.append(
                'column index({}) is out of range of row({})\' cells\' count {}'.format(column_index, self.row_num,
                                                                                        len(self.cells)))
            return None

        return self.cells[column_index]

    def has_content(self):
        if not self.is_inited():
            return False

        for cell in self.cells:
            if len(cell) > 0:
                return True

        return False

    def string(self, splitter: str = ',', line_ending: str = '\r\n'):
        return splitter.join(self.cells) + line_ending


class Form:
    def __init__(self, err: Error):
        self.err = err
        self.title_row = Row(-1, [])
        self.data_rows: List[Row] = []

    def __repr__(self):
        return '\nForm<title: {}, data: {}>' \
            .format(self.title_row, self.data_rows)

    def __str__(self):
        return self.__repr__()

    def row_with_num(self, row_num=0):
        return first_match(lambda x: x.row_num == row_num, self.data_rows).data

    def column_index_with_title(self, title=''):
        column_index = self.title_row.index(title)
        if column_index < 0:
            self.err.append('can not find title "{}"'.format(title))
        return column_index

    def title_to_column_index_mapping(self, titles: List[str]):
        if self.err.has_error():
            return

        mapping = {}
        for title in titles:
            index = self.column_index_with_title(title)
            if self.err.has_error():
                return
            mapping[title] = index

        return mapping

    def set_title_row(self, row_num=1, titles: List[any] = None, do_strip=True):
        if titles is None:
            titles = []
        r = self.title_row
        if r.is_inited():
            self.err.append('title row has already been included')
        else:
            self.title_row = Row(row_num, titles, do_strip)

    def append_data_row(self, row_num=2, cells: List[any] = None, do_strip=True):
        if cells is None:
            cells = []
        if self.row_with_num(row_num) is not None:
            self.err.append('row with number {} has already been included'.format(row_num))
        else:
            if not self.title_row.is_inited():
                self.err.append('should include title row before append data')
                return
            diff = len(self.title_row.cells) - len(cells)
            while diff > 0:
                cells.append(None)
                diff -= 1
            self.data_rows.append(Row(row_num, cells, do_strip))

    def row(self, row_index=0):
        if self.err.has_error():
            return None
        if row_index >= len(self.data_rows) or row_index < 0:
            self.err.append('row index {} is out of range'.format(row_index))
            return None
        return self.data_rows[row_index]

    def cell(self, row_index=0, column_index=0):
        r = self.row(row_index)
        if r is None:
            return None

        return r.cell(column_index, self.err)

    def cell_with_title(self, row_index=0, title=''):
        if self.err.has_error():
            return
        column_index = self.column_index_with_title(title)
        return self.cell(row_index, column_index)

    def cell_with_title_must_have(self, row_index=0, title=''):
        if self.err.has_error():
            return

        cell = self.cell_with_title(row_index, title)
        if self.err.has_error():
            return

        if cell is None:
            self.err.append('empty cell at row {} with column name {}'.format(self.data_rows[row_index].row_num, title))
            return

        return cell

    def find_row_by_column(self, column_title: str, column_value: any):
        column_index = self.title_row.index(column_title)
        if column_index < 0:
            self.err.append('column with title({}) is not found'.format(column_title))
            return None

        r = first_match(lambda x: x.cells[column_index] == column_value, self.data_rows)
        if r.data is None:
            self.err.append('cannot find row with column value({}) in column (title: {})'
                            .format(column_value, column_title))

        return r

    def row_with_value(self, column_title: str, column_value: any):
        r = self.find_row_by_column(column_title, column_value)
        return None if self.err.has_error() else r.data

    def row_index_with_value(self, column_title: str, column_value: any):
        r = self.find_row_by_column(column_title, column_value)
        return -1 if self.err.has_error() else r.index

    def cells_lookup(self, title, value_of_title, other_titles: List[any] = None):
        if other_titles is None:
            other_titles = []
        if self.err.has_error():
            return None
        r: Row = self.row_with_value(title, value_of_title)

        if self.err.has_error():
            return None

        results = []
        for t in other_titles:
            i = self.title_row.index(t)
            if i < 0:
                self.err.append('title({}) is not found'.format(t))
                return None
            else:
                results.append(r.cell(i, self.err))
                if self.err.has_error():
                    return None
        return results

    def cell_lookup(self, title, value_of_title, other_title=''):
        cells = self.cells_lookup(title, value_of_title, [other_title])
        if self.err.has_error() or cells is None or len(cells) == 0:
            return None

        return cells[0]

    def data_row_nums_with_content(self):
        nums = []
        for r in self.data_rows:
            if r.has_content():
                nums.append(r.row_num)
        return nums

    def export_as_csv_file(self, file_path: str, splitter: str = ',', line_ending: str = '\r\n'):
        with open(file_path, "w") as f:
            f.write(self.title_row.string(splitter, line_ending))

            for row in self.data_rows:
                f.write(row.string(splitter, line_ending))
