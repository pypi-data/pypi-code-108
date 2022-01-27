# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Gather various item modules to encourage sharing.
"""
from typing import List, Tuple, Callable, Any
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
import copy
import contextlib
from . import colors
from sympathy.widgets import utils as widget_utils

EditRole = QtCore.Qt.EditRole
DisplayRole = QtCore.Qt.DisplayRole
ToolTipRole = QtCore.Qt.ToolTipRole
TextAlignmentRole = QtCore.Qt.TextAlignmentRole
BackgroundRole = QtCore.Qt.BackgroundRole

Vertical = QtCore.Qt.Vertical
Horizontal = QtCore.Qt.Horizontal

AlignLeft = QtCore.Qt.AlignLeft

ItemIsSelectable = QtCore.Qt.ItemIsSelectable
ItemIsEnabled = QtCore.Qt.ItemIsEnabled
ItemIsEditable = QtCore.Qt.ItemIsEditable

QModelIndex = QtCore.QModelIndex


# Utils.

def indexed_header_display(section, orientation, role):
    return str(section)


def header_orientations():
    return [Vertical, Horizontal]


def pairs(xs: List, ys: List):
    return [(x, y) for x in xs for y in ys]


# Mixins for QAbstractTableModel and in some cases QAbstactItemModel.
# These are inherited to customize the behavior of a model.
# Any new arguments are keywords, the idea is to make it possible to
# combine mixins to get the desired behavior to avoid duplication when
# creating new subclasses.

class HeaderDataMixin:
    # Base class.
    def headerData(self, section, orientation, role=DisplayRole):
        return super().headerData(section, orientation, role)


class IndexVerticalHeaderData(HeaderDataMixin):
    def headerData(self, section, orientation, role=DisplayRole):
        if (orientation, role) == (DisplayRole, Vertical):
            return indexed_header_display(section, orientation, role)
        return super().headerData(section, orientation, role)


class LeftAlignHeaderData(HeaderDataMixin):
    def headerData(self, section, orientation, role=DisplayRole):
        if (orientation, role) in pairs(header_orientations(),
                                        [TextAlignmentRole]):
            return AlignLeft
        return super().headerData(section, orientation, role)


class FixedHorizontalHeaderData(HeaderDataMixin):
    def __init__(self, *args, horizontal_headers, **kwargs):
        super().__init__(*args, **kwargs)
        super().removeColumns(0, self.columnCount())
        super().insertColumns(0, len(horizontal_headers))
        for i, text in enumerate(horizontal_headers):
            self.setHeaderData(
                i, Horizontal, text, role=DisplayRole)

    def insertColumns(self, column, count, parent=QModelIndex()):
        return False

    def removeColumns(self, column, count, parent=QModelIndex()):
        return False


class FlagsMixin:
    # Base class.

    def flags(self, index):
        return super().flags(index)


class EditFlags(FlagsMixin):
    def __init__(self, *args,
                 edit_flags=(
                     ItemIsSelectable |
                     ItemIsEnabled |
                     ItemIsEditable),
                 **kwargs):
        self._edit_flags = edit_flags
        super().__init__(*args, **kwargs)

    def flags(self, index):
        return self._edit_flags


class DataMixin:
    # Base class.

    def data(self, index, role=DisplayRole):
        return super().data(index, role)


class ToListMixin:
    def to_list(self, role=DisplayRole):
        index = range(self.rowCount())
        n_columns = self.columnCount()
        if n_columns <= 0:
            return [[] for _ in index]
        return [[self.data(self.index(row, column), role)
                 for column in range(n_columns)] for row in index]

    def from_list(self, rows, role=EditRole):
        """
        Set from list, probably very inefficent for large data due to
        setting values one by one, triggering dataChanged.
        """
        row = self.rowCount()
        self.insertRows(row, len(rows))
        for row, values in enumerate(rows, row):
            for column, value in zip(range(self.columnCount()), values):
                self.setData(self.index(row, column), value, role)


class WarnColumnEmptyData(DataMixin):
    """
    Warn when selected column is empty using color and tooltip.
    """
    def __init__(self, *args, non_empty_column=0, **kwargs):
        self._non_empty_column = non_empty_column
        super().__init__(*args, **kwargs)

    def data(self, index, role=DisplayRole):
        def empty():
            if self.columnCount() <= self._non_empty_column:
                return True
            data = self.data(
                self.index(index.row(), self._non_empty_column), DisplayRole)
            data = str(data or '').strip()
            return not bool(data)

        if role == BackgroundRole:
            if empty():
                return QtGui.QBrush(colors.WARNING_BG_COLOR)
        elif role == ToolTipRole:
            if empty():
                name = self.headerData(0, Horizontal, DisplayRole)
                return f'{name} is empty, this row is ignored'
        return super().data(index, role)


# Table models.


class TableData:
    """
    Simplified interface for customizing TableModel.
    Can be implemented for various tabular data models.

    To avoid expensive updates on a model, TableData
    can be built in advance and set using setTableData.

    Base class.
    """

    def row_count(self):
        raise NotImplementedError()

    def column_count(self):
        raise NotImplementedError()

    def data(self, row, column, role=DisplayRole):
        raise NotImplementedError()

    def set_data(self, row, column, value, role=EditRole):
        raise NotImplementedError()

    def header_data(self, section, orientation, role=DisplayRole):
        raise NotImplementedError()

    def set_header_data(self, section, orientation, value, role=EditRole):
        raise NotImplementedError()

    def insert_rows(self, row, count):
        raise NotImplementedError()

    def remove_rows(self, row, count):
        raise NotImplementedError()

    def insert_columns(self, column, count):
        raise NotImplementedError()

    def remove_columns(self, column, count):
        raise NotImplementedError()


class ListTableData(TableData):
    """
    General purpose, editable TableData.
    """
    def __init__(self):
        self._item_factory = dict
        self._rows = []
        self._horizontal_headers = []
        self._vertical_headers = []

    def row_count(self):
        return len(self._vertical_headers)

    def column_count(self):
        return len(self._horizontal_headers)

    def data(self, row, column, role=DisplayRole):
        return self._rows[row][column].get(role)

    def set_data(self, row, column, value, role=EditRole):
        self._rows[row][column][role] = value

    def _orientation_header(self, orientation):
        return {
            Vertical: self._vertical_headers,
            Horizontal: self._horizontal_headers,
        }[orientation]

    def header_data(self, section, orientation, role=DisplayRole):
        headers = self._orientation_header(orientation)
        return headers[section].get(role)

    def set_header_data(self, section, orientation, value, role=EditRole):
        headers = self._orientation_header(orientation)
        headers[section][role] = value

    def _count_factory(self, n):
        return self._range_factory(range(n))

    def _rows_range(self):
        return range(self.row_count())

    def _columns_range(self):
        return range(self.column_count())

    def _range_factory(self, items):
        return [self._item_factory() for _ in items]

    def insert_rows(self, row, count):
        rows = [self._range_factory(self._columns_range())
                for _ in range(count)]
        self._rows[row:row] = rows
        self._vertical_headers[row:row] = self._count_factory(count)

    def remove_rows(self, row, count):
        self._rows[row:row + count] = []
        self._vertical_headers[row:row + count] = []

    def _transposed(self, data):
        return list(zip(*data))

    def _assign_columns(self, index, value):
        columns = self._transposed(self._rows)
        columns[index] = value
        self._rows = list(map(list, zip(*columns)))

    def insert_columns(self, column, count):
        if self.row_count() > 0:
            columns = [self._range_factory(self._rows_range())
                       for _ in range(count)]
            self._assign_columns(slice(column, column), columns)
        self._horizontal_headers[column:column] = self._count_factory(
            count)

    def remove_columns(self, column, count):
        if self.row_count() > 0:
            self._assign_columns(slice(column, column), [])
        self._horizontal_headers[column:column + count] = []


class SyTableData(TableData):
    """
    Basic, read-only TableData for Sympathy Table.
    Not suitable for large tables.

    Illustrates a basic case of read-only TableData and
    formatting of cells depending on their value type.
    """

    # TODO(erik): generalize handling of display and tooltip formatting
    # for other kinds of typed widgets.

    def __init__(self, table: 'sympathy.api.table.File'):
        self._table = table
        self._headers = table.column_names()
        self._decimals = 4

    def row_count(self):
        return self._table.number_of_rows()

    def column_count(self):
        return self._table.number_of_columns()

    def _data(self, row, column):
        return self._table[self._headers[column]][row]

    def data(self, row, column, role=DisplayRole):
        res = None
        if role == DisplayRole:
            res = self._data(row, column)
            res = widget_utils.format_data(self._data(row, column),
                                           self._decimals)
        elif role == ToolTipRole:
            text = widget_utils.format_data(self._data(row, column))
            res = QtGui.QTextDocumentFragment.fromPlainText(text).toHtml()
        return res

    def header_data(self, section, orientation, role=DisplayRole):
        res = None
        if orientation == Horizontal:
            if role == DisplayRole:
                res = self._headers[section]
        return res


class TableModel(QtCore.QAbstractTableModel):
    """
    General Table Model which can use TableData as underlying
    storage.
    """

    def __init__(self, *args, table_data: TableData = None,
                 parent=None, **kwargs):
        if table_data is None:
            table_data = ListTableData()
        self._table_data = table_data
        super().__init__(parent)

    def rowCount(self, index=None):
        return self._table_data.row_count()

    def columnCount(self, index=None):
        return self._table_data.column_count()

    def _value_to_string(self, value):
        res = ''
        if value is not None:
            res = str(value)
        return res

    def data(self, index, role=DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        res = self._table_data.data(row, col, role)
        if role == DisplayRole:
            if res is None:
                res = self._table_data.data(row, col, EditRole)
            res = self._value_to_string(res)
        return res

    def setData(self, index, value, role=EditRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        self._table_data.set_data(row, col, value, role)
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role=DisplayRole):
        res = self._table_data.header_data(section, orientation, role)
        if res is None and role == DisplayRole:
            res = self._table_data.header_data(section, orientation, EditRole)
            if res is not None:
                res = self._value_to_string(res)
        if res is None:
            res = super().headerData(section, orientation, role)
        return res

    def setHeaderData(self, section, orientation, value, role=EditRole):
        self._table_data.set_header_data(section, orientation, value, role)
        self.headerDataChanged.emit(orientation, section, section)
        return True

    @contextlib.contextmanager
    def _do_reset_model(self):
        try:
            self.beginResetModel()
            yield
        finally:
            self.endResetModel()

    @contextlib.contextmanager
    def _do_insert_rows(self, parent, first, last):
        try:
            self.beginInsertRows(parent, first, last)
            yield
        finally:
            self.endInsertRows()

    @contextlib.contextmanager
    def _do_remove_rows(self, parent, first, last):
        try:
            self.beginRemoveRows(parent, first, last)
            yield
        finally:
            self.endRemoveRows()

    @contextlib.contextmanager
    def _do_insert_columns(self, parent, first, last):
        try:
            self.beginInsertColumns(parent, first, last)
            yield
        finally:
            self.endInsertColumns()

    @contextlib.contextmanager
    def _do_remove_columns(self, parent, first, last):
        try:
            self.beginRemoveColumns(parent, first, last)
            yield
        finally:
            self.endRemoveColumns()

    def clear(self):
        self.removeRows(0, self.rowCount())
        self.removeColumns(0, self.columnCount())

    def _valid_insert_i(self, i, bound):
        return 0 <= i and i <= bound

    def _valid_remove_i(self, i, count, bound):
        return self._valid_insert_i(i, bound - count)

    def insertRows(self, row, count, parent=QModelIndex()):
        if not self._valid_insert_i(row, self.rowCount()):
            return False
        with self._do_insert_rows(parent, row, row + count - 1):
            self._table_data.insert_rows(row, count)
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        if not self._valid_remove_i(row, count, self.rowCount()):
            return False
        with self._do_remove_rows(parent, row, row + count - 1):
            self._table_data.remove_rows(row, count)
        return True

    def insertColumns(self, column, count, parent=QModelIndex()):
        if not self._valid_insert_i(column, self.columnCount()):
            return False
        with self._do_insert_columns(parent, column, column + count - 1):
            self._table_data.insert_columns(column, count)
        return True

    def removeColumns(self, column, count, parent=QModelIndex()):
        if not self._valid_remove_i(column, count, self.columnCount()):
            return False
        with self._do_remove_columns(parent, column, column + count - 1):
            self._table_data.remove_columns(column, count)
        return True

    def setTableData(self, table_data: TableData):
        with self._do_reset_model():
            self._table_data = table_data

    def tableData(self) -> TableData:
        return self._table_data


# Concrete Table Models.


class StandardTableModel(IndexVerticalHeaderData,
                         LeftAlignHeaderData,
                         QtGui.QStandardItemModel):
    pass


class EditTableModel(
        ToListMixin,
        IndexVerticalHeaderData,
        LeftAlignHeaderData,
        EditFlags,
        TableModel):
    pass


class DictTableModel(
        FixedHorizontalHeaderData,
        EditTableModel):
    """
    Intended use case is a fixed header with 2 columns.
    Otherwise the dict name is inappropriate.
    """
    pass


class KeyDictTableModel(
        WarnColumnEmptyData,
        DictTableModel):
    """
    Require non-empty keys.
    """
    pass
