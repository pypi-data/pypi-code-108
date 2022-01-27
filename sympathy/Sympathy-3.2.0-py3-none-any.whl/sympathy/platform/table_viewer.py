# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
import os.path
import re
import datetime
import operator
import itertools
import collections
import fnmatch
import enum
import warnings

from sympathy.utils import prim
from sympathy.widgets import utils as widget_utils
from Qt import QtCore, QtGui, QtWidgets
from sympathy.platform import qt_compat2
from sympathy.platform import settings

import numpy as np
from sympathy.platform import widget_library as sywidgets
from sympathy.typeutils import table
from . viewerbase import ViewerBase
from .. utils import dtypes
from .. utils import search


def _typenames():
    """
    Preserving classic order and putting any future additions last So that the
    order is well defined, just in case new types are added without also
    updating the desired order.
    """
    classic_order = [
        'bool',
        'integer',
        'float',
        'complex',
        'text',
        'bytes',
        'datetime',
        'timedelta'
    ]

    typenames = dtypes.typenames()

    def sort_key(typename):
        if typename in classic_order:
            return (classic_order.index(typename), 0)
        else:
            return (len(classic_order), typenames.index(typename))

    return list(sorted(typenames, key=sort_key))


DTYPE_COLOR = [QtGui.QColor.fromHsvF(i / len(_typenames()), 0.18, 0.9)
               for i in range(len(_typenames()))]
COLUMN_COLORS = {kind: color for kind, color in zip(
    _typenames(), DTYPE_COLOR)}

DATA_FONT = QtGui.QFont('Courier')
VALID_AS_X = ('f', 'i', 'u', 'M')
VALID_AS_Y = ('f', 'i', 'u', 'b', 'm')
VALID_AS_HIST = ('f', 'i', 'u', 'b', 'M', 'S', 'U')


def dtype_color(dtype):
    try:
        dtypename = dtypes.typename_from_kind(dtype.kind)
        res = COLUMN_COLORS.get(dtypename, None)
    except KeyError:
        res = None
    return res


def _matplotlib():
    qt_compat2.backend.use_matplotlib_qt()
    import matplotlib.dates
    import matplotlib.figure
    import matplotlib.backends.backend_qt5agg
    import matplotlib.offsetbox
    return matplotlib


def _widget_mpl():
    qt_compat2.backend.use_matplotlib_qt()
    from sympathy.widgets import mpl as widget_mpl
    return widget_mpl


def fuzzy_list_filter(pattern, items):

    if pattern:
        filter_ = search.fuzzy_free_pattern(pattern)
        display = []
        for row, col_item in enumerate(items):
            if isinstance(col_item, list):
                is_match = any(
                    [search.matches(
                        filter_,
                        widget_utils.format_data(item))
                     for item in col_item])
            else:
                is_match = search.matches(
                    filter_,
                    widget_utils.format_data(col_item))
            if is_match:
                display.append(row)
    else:
        display = range(len(items))

    return display


def glob_list_filter(pattern, items):

    def globmatch(item, pattern):
        return fnmatch.fnmatchcase(item.lower(), pattern.lower())

    if pattern:
        display = []

        for row, col_item in enumerate(items):
            if isinstance(col_item, list):
                is_match = any(globmatch(TableModel.format_data(item), pattern)
                               for item in col_item)
            else:
                is_match = globmatch(TableModel.format_data(col_item), pattern)
            if is_match:
                display.append(row)
    else:
        display = range(len(items))
    return display


def meta_filter(pattern, columns):
    identifiers = ['a', 'c', '*']

    if (pattern.startswith(':') and len(pattern) >= 2 and
            pattern[1] in identifiers):
        # prefix search case
        startend = []
        patterns = []
        for m in re.finditer(r':([ac*])\s', pattern):
            startend.extend([m.start(), m.end()])
            patterns.append(m.group(1))
        if len(startend):
            startend.pop(0)
            startend.append(len(pattern))

        startend = [slice(startend[i], startend[i+1])
                    for i in range(len(startend)) if not i % 2]
        patterns = [(p, pattern[se]) for p, se in zip(patterns, startend)]

    else:
        # default to column search
        patterns = [('c', pattern)]

    org_columns = columns[:]  # copy original columns

    for type, pat in patterns:
        pat = pat.strip(' ')
        if type == 'c':
            # handle column search
            names = [col.name for col in columns]
            search_in = [names]
        elif type == 'a':
            # handle attribute search
            keys = [col.attrs.keys() for col in columns]
            values = [col.attrs.values() for col in columns]
            search_in = [keys, values]
        else:
            # handle search in both attributes and column names
            names = [col.name for col in columns]
            keys = [col.attrs.keys() for col in columns]
            values = [col.attrs.values() for col in columns]
            search_in = [names, keys, values]
        # apply search
        result = set()
        for items in search_in:
            result.update(apply_filter(pat, items))
        columns = [columns[idx] for idx in result]

    filtered_item_indexes = [org_columns.index(col) for col in columns]
    return filtered_item_indexes


def apply_filter(pat, items):
    patterns = pat.split(',')
    filtered_item_indexes = set()
    for p in patterns:
        if '*' in p or '?' in p:
            display = glob_list_filter(p, items)
        else:
            display = fuzzy_list_filter(p, items)
        filtered_item_indexes.update(display)
    return filtered_item_indexes


class TransposedModel(QtCore.QAbstractTableModel):
    def __init__(self, base_model, parent=None):
        super().__init__(parent)
        self._base_model = base_model
        self._base_model.layoutChanged.connect(self.layoutChanged)
        self._base_model.modelAboutToBeReset.connect(self.beginResetModel)
        self._base_model.modelReset.connect(self.endResetModel)

    def _transpose_index(self, index):
        return self._base_model.index(
            index.column(), index.row(), index.parent())

    def base_model(self):
        return self._base_model

    def rowCount(self, index):
        return self._base_model.columnCount(self._transpose_index(index))

    def columnCount(self, index):
        return self._base_model.rowCount(self._transpose_index(index))

    def data(self, index, role):
        return self._base_model.data(self._transpose_index(index), role)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            orientation = QtCore.Qt.Horizontal
        else:
            orientation = QtCore.Qt.Vertical
        return self._base_model.headerData(section, orientation, role)

    def column_names(self):
        return self._base_model.column_names()

    def column_name(self, row, column):
        """
        Return name for table column with index row.

        This method can be used to get the column name for a cell without
        checking if the model is transposed or not.
        """
        if 0 <= row < len(self.column_names()):
            return self.column_names()[row]
        else:
            raise IndexError("Column {} does not exist.".format(row))

    def table(self):
        return self._base_model.table()

    def set_decimals(self, decimals):
        return self._base_model.set_decimals(decimals)

    def reset(self):
        self.beginResetModel()
        self._base_model.reset()
        self.endResetModel()


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._show_colors = True

        self._table = None
        self._decimals = 4
        self._headers = None
        self._row_count = 0
        self._column_count = 0

        # max row number due to qt bug
        self._max_row_limit = 71582788

        self._cache = {}
        # self._cnt = 0

    def table(self):
        return self._table

    def set_table(self, table_):
        if table is None:
            return

        self.beginResetModel()
        self._table = table_
        self._headers = table_.column_names()
        self._row_count = self._table.number_of_rows()
        self._column_count = self._table.number_of_columns()
        self._cache = {}
        self._update_cache(0, 0)
        self.endResetModel()

    def set_decimals(self, decimals):
        self._decimals = decimals

    @classmethod
    def format_data(cls, data, decimals=None):
        return widget_utils.format_data(data, decimals)

    def set_show_colors(self, show):
        self._show_colors = show

    def column_names(self):
        if self._table is None:
            return []
        else:
            return self._table.column_names()

    def column_name(self, row, column):
        """
        Return name for table column with index column.

        This method can be used to get the column name for a cell without
        checking if the model is transposed or not.
        """
        if 0 <= column < len(self.column_names()):
            return self.column_names()[column]
        else:
            raise IndexError("Column {} does not exist.".format(column))

    def rowCount(self, qmodelindex):
        if self._row_count > self._max_row_limit:
            return self._max_row_limit
        return self._row_count

    def columnCount(self, qmodelindex):
        return self._column_count

    def data(self, qmodelindex, role):
        if not qmodelindex.isValid():
            return None
        row = qmodelindex.row()
        col = qmodelindex.column()
        if role == QtCore.Qt.DisplayRole:
            if row < self._max_row_limit - 1:
                try:
                    data = self._cache[(row, col)]
                except KeyError:
                    self._update_cache(row, col)
                    data = self._cache[(row, col)]
                element = self.format_data(data, self._decimals)
            else:
                element = 'Data truncated!'
            return element
        elif role == QtCore.Qt.ToolTipRole:
            if row < self._max_row_limit - 1:
                text = self.format_data(self._cache[(row, col)])
            else:
                text = 'Data truncated since maximum view limit reached!'
            # Escape HTML characters in a way that is compatible with QToolTip.
            return QtGui.QTextDocumentFragment.fromPlainText(text).toHtml()
        elif role == QtCore.Qt.BackgroundRole:
            if self._show_colors:
                if row < self._max_row_limit - 1:
                    return self._column_color(col)
                return QtGui.QColor.fromRgb(228, 186, 189)
            else:
                return None
        elif role == QtCore.Qt.FontRole:
            return DATA_FONT
        return None

    def _create_column_tooltip_string(self, column_name):
        column_type = self._table.column_type(column_name)
        tooltip_string = '"{}"\n\nType: {} ({})'.format(
            column_name, dtypes.typename_from_kind(column_type.kind),
            column_type)
        attrs = self._table.get_column_attributes(column_name)
        attrs_string = '\n'.join(
            ['{}: {}'.format(k, v) for k, v in attrs.items()])
        if attrs_string:
            tooltip_string += '\n\nAttributes:\n{}'.format(attrs_string)
        return tooltip_string

    def _column_color(self, column):
        column_type = self._table.column_type(self._headers[column])
        return dtype_color(column_type)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._headers[section]
            elif role == QtCore.Qt.ToolTipRole:
                return self._create_column_tooltip_string(
                    self._headers[section])
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(section)
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def attributes(self):
        attrs = self._table.get_table_attributes() or {}
        return ['{}: {}'.format(k, v) for k, v in attrs.items()]

    def _update_cache(self, row, col, row_cache_size=1000,
                      col_cache_size=100, max_cache_size=1000000):
        def lt(x, y): return x < y

        def gt(x, y): return x > y

        def bound_fn(rel, val, bound): return val if rel(val, bound) else bound

        def lower_bound(val, bound): return bound_fn(gt, val, bound)

        def upper_bound(val, bound): return bound_fn(lt, val, bound)

        start_row = lower_bound(row - row_cache_size // 2, 0)
        end_row = upper_bound(row + row_cache_size // 2, self._row_count)

        start_col = lower_bound(col - col_cache_size // 2, 0)
        end_col = upper_bound(col + col_cache_size // 2, self._column_count)

        rows_to_cache = range(start_row, end_row)
        cols_to_cache = range(start_col, end_col)

        real_row_col = itertools.product(rows_to_cache, cols_to_cache)
        norm_row_col = itertools.product(
            range(end_row - start_row), range(end_col - start_col))

        table_sliced = self._table[start_row:end_row, start_col:end_col]
        if len(self._cache) > max_cache_size:
            self._cache = {}

        columns = [table_sliced.get_column_to_array(name)
                   for name in table_sliced.column_names()]

        self._cache.update({(row, col): columns[n_col][n_row]
                            for (row, col), (n_row, n_col) in zip(
                                    real_row_col, norm_row_col)})

    def reset(self):
        self.beginResetModel()
        self.endResetModel()


class AttributeModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._attributes = None
        self._headers = None
        self._row_count = 0
        self._column_count = 0

    def set_attributes(self, attributes_):
        self.beginResetModel()
        if not isinstance(attributes_, dict):
            return
        self._attributes = [(key, value)
                            for key, value in attributes_.items()]

        self._headers = ['Name', 'Value']
        self._column_count = 2
        self._row_count = len(self._attributes)
        self.endResetModel()

    def columnCount(self, qmodelindex):
        return self._column_count

    def rowCount(self, qmodelindex):
        return self._row_count

    def data(self, qmodelindex, role):
        if not qmodelindex.isValid():
            return None
        row = qmodelindex.row()
        col = qmodelindex.column()
        if role == QtCore.Qt.DisplayRole:
            data = self._attributes[row][col]
            return data
        elif role == QtCore.Qt.ToolTipRole:
            # Escape HTML characters in a way that is compatible with QToolTip.
            return QtGui.QTextDocumentFragment.fromPlainText(
                str(self._attributes[row][col])).toHtml()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._headers[section]
            elif role == QtCore.Qt.ToolTipRole:
                return self._headers[section]
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft

        return super().headerData(section, orientation, role)

    def reset(self):
        self.beginResetModel()
        self.endResetModel()


class TableViewerPreviewTable(sywidgets.EnhancedPreviewTable):
    def __init__(self, model=None, filter_function=None, parent=None):
        super().__init__(model, filter_function, parent)
        self._preview_table.setMinimumHeight(300)
        self.row_column_legend = sywidgets.RowColumnLegend()
        self.add_widget_to_legend(self.row_column_legend, on_left=True)

    def table(self):
        return self._model.table()

    def show_decimals(self, decimals):
        try:
            self._model.set_decimals(decimals)
        except AttributeError:
            return
        self._model.reset()
        # (Bene) the Qt resize is extremely costly for large tables
        # self._preview_table.resizeColumnsToContents()

    def set_row_column_legend(self, row, column):
        self.row_column_legend.set_row_column(row, column)


class CursorWidgetToolButton(sywidgets.WidgetToolButton):

    n_cursors_changed = QtCore.Signal(int)
    show_stats_toggled = QtCore.Signal(bool)
    show_delta_toggled = QtCore.Signal(bool)
    snap_toggled = QtCore.Signal(bool)

    _n_cursors_labels = [
        '0: Off',
        '1: On',
        '2: On',
    ]

    def __init__(self, parent=None):

        widget = QtWidgets.QWidget()
        super().__init__(widget, parent=parent)
        layout = QtWidgets.QVBoxLayout()

        widget.setContentsMargins(2, 2, 2, 2)
        layout.setContentsMargins(0, 0, 0, 0)

        n_cursors_layout = QtWidgets.QHBoxLayout()
        n_cursors_label = QtWidgets.QLabel('Cursors')

        self._n_cursors_combo = QtWidgets.QComboBox()

        for k in self._n_cursors_labels:
            self._n_cursors_combo.addItem(k)

        n_cursors_layout.addWidget(n_cursors_label)
        n_cursors_layout.addWidget(self._n_cursors_combo)

        layout.addLayout(n_cursors_layout)

        self._snap_check = QtWidgets.QCheckBox('Snap')
        self._snap_check.setToolTip(
            'Snap to data points on the x-axis')
        self._show_stats_check = QtWidgets.QCheckBox('Show Stats')
        self._show_stats_check.setToolTip(
            'Show stats of region between cursors (requires 2 cursors)')
        self._show_delta_check = QtWidgets.QCheckBox('Show Delta')
        self._show_delta_check.setToolTip(
            'Show delta between cursors (requires 2 cursors)')

        layout.addWidget(self._snap_check)
        layout.addWidget(self._show_stats_check)
        layout.addWidget(self._show_delta_check)

        widget.setLayout(layout)

        self.setCheckable(True)

        icon = QtGui.QIcon(
            prim.get_icon_path('actions/view-plot-scatter-cursor-symbolic.svg'))
        self.setIcon(icon)
        self.setToolTip('Show Cursor Control')
        self._n_cursors_changed(0)
        self._n_cursors_combo.currentIndexChanged[int].connect(
            self._n_cursors_changed)
        self._show_stats_check.toggled.connect(self.show_stats_toggled)
        self._show_delta_check.toggled.connect(self.show_delta_toggled)
        self._snap_check.toggled.connect(self.snap_toggled)

    def get_snap(self):
        return self._snap_check.value()

    def get_n_cursors(self):
        return self._n_cursors_combo.value()

    def get_show_stats(self):
        return self._show_stats_check.isChecked()

    def get_show_delta(self):
        return self._show_delta_check.isChecked()

    def _n_cursors_changed(self, value):
        self.n_cursors_changed.emit(value)
        self.setChecked(value > 0)
        self._show_stats_check.setEnabled(value > 1)
        self._show_delta_check.setEnabled(value > 1)


class TableViewer(ViewerBase):
    def __init__(self, table_=None, console=None, plot=True,
                 show_title=True, parent=None):
        super().__init__(parent)
        self._table_model = TableModel(self)
        self._attribute_model = AttributeModel(self)
        self._model = self._table_model

        self.has_plot = plot
        self._show_title = show_title

        self._console = console
        self._data_preview = TableViewerPreviewTable(
            model=self._model, filter_function=meta_filter)

        self._table_name_label = QtWidgets.QLabel()
        self._title_layout = QtWidgets.QHBoxLayout()
        self._title_layout.addWidget(QtWidgets.QLabel("Name: "))
        self._title_layout.addWidget(self._table_name_label)
        self._title_layout.addStretch()

        self._legend = Legend()

        if self._show_title:
            self._data_preview.add_layout_to_layout(self._title_layout,
                                                    on_top=True)
        self._data_preview.add_widget_to_legend(self._legend)

        hsplitter = QtWidgets.QSplitter()
        hsplitter.addWidget(self._data_preview)
        hsplitter.setCollapsible(0, False)

        # Figure
        if self.has_plot:
            self._plot = ViewerPlot(self._table_model)
            hsplitter.addWidget(self._plot)
            hsplitter.setCollapsible(1, False)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(hsplitter)
        if self._console is not None:
            layout.addWidget(self._console)
        self.setLayout(layout)

        table_toolbar = self._data_preview.toolbar()

        # Jump to row menu
        jump_to_row_go_button = QtWidgets.QPushButton('Go')
        jump_to_row_go_button.clicked.connect(self._handle_jump_to_row)
        self.jump_to_row_value = QtWidgets.QSpinBox()
        self.jump_to_row_value.setRange(0, 100000)

        jump_to_row_widget = QtWidgets.QWidget(self)
        jump_to_row_widget.setContentsMargins(2, 2, 2, 2)
        jump_to_row_layout = QtWidgets.QHBoxLayout()
        jump_to_row_layout.setContentsMargins(0, 0, 0, 0)
        jump_to_row_layout.addWidget(self.jump_to_row_value)
        jump_to_row_layout.addWidget(jump_to_row_go_button)
        jump_to_row_widget.setLayout(jump_to_row_layout)

        self.jump_to_row_menu = QtWidgets.QMenu(table_toolbar)
        jump_to_row_action = QtWidgets.QWidgetAction(self)
        jump_to_row_action.setDefaultWidget(jump_to_row_widget)
        self.jump_to_row_menu.addAction(jump_to_row_action)

        jump_to_row_button = QtWidgets.QToolButton()
        jump_to_row_button.setMenu(self.jump_to_row_menu)
        jump_to_row_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        jump_to_row_button_action = QtWidgets.QWidgetAction(self)
        jump_to_row_button_action.setDefaultWidget(jump_to_row_button)
        icon = QtGui.QIcon(
            prim.get_icon_path('actions/view-jump-to-row-symbolic.svg'))
        jump_to_row_button.setIcon(icon)
        table_toolbar.addAction(jump_to_row_button_action)
        jump_to_row_button.setToolTip(
            'Enter a row number to jump to that row.')

        self._toggle_attributes_action = table_toolbar.add_action(
            text='Show &attributes',
            icon_name='actions/table-attributes.svg',
            tooltip_text='Show table attributes',
            is_checkable=True)
        self._toggle_attributes_action.toggled.connect(
            self._handle_toggle_attributes)

        self._toggle_transpose_action = table_toolbar.add_action(
            text='&Transpose view',
            icon_name='actions/view-transpose-symbolic.svg',
            tooltip_text='Transpose view',
            is_checkable=True)
        self._toggle_transpose_action.toggled.connect(
            self._handle_toggle_transpose)

        copy_icon = 'actions/fontawesome/svgs/regular/copy.svg'
        self._data_preview.preview_table().add_context_menu_action(
            'Copy',
            self.copy_selection,
            copy_icon,
            validate_callback=self.validate_copy,
            key_sequence=QtGui.QKeySequence.Copy)

        self._data_preview.preview_table().add_context_menu_action(
            'Copy with column names',
            self.copy_selection_with_column_names,
            copy_icon,
            validate_callback=self.validate_copy_with_column_names)

        self._data_preview.preview_table().add_context_menu_action(
            'Copy column name',
            self.copy_column_name,
            copy_icon,
            validate_callback=self.validate_copy_column_names)

        self._data_preview.preview_table().add_context_menu_action(
            'Copy all column names',
            self.copy_column_names,
            copy_icon,
            validate_callback=self.validate_copy_column_names)

        if self.has_plot:
            self._show_none_action = sywidgets.create_action(
                text='No plot',
                icon_name='actions/view-plot-none-symbolic.svg',
                tooltip_text='No plot',
                triggered=self.show_none)

            self._show_line_action = sywidgets.create_action(
                text='Line plot',
                icon_name='actions/view-plot-line-symbolic.svg',
                tooltip_text='Line plot',
                triggered=self.show_line)

            self._show_hist_action = sywidgets.create_action(
                text='Histogram plot',
                icon_name='actions/view-plot-hist-symbolic.svg',
                tooltip_text='Histogram',
                triggered=self.show_hist)

            self._show_plot_button = sywidgets.MenuToolButton(
                self._show_none_action, [
                    self._show_none_action,
                    self._show_line_action,
                    self._show_hist_action])
            table_toolbar.addWidget(self._show_plot_button)

            self._show_none_action.trigger()

            self._plot.plot_type_changed.connect(
                self._handle_plot_type_changed)

            # init context menus
            self._data_preview.preview_table().add_context_menu_action(
                'Plot column as x',
                self.plot_as_x,
                'actions/view-plot-x-axis-symbolic.svg',
                validate_callback=self.validate_as_x)
            self._data_preview.preview_table().add_context_menu_action(
                'Plot column as y',
                self.plot_as_y,
                'actions/view-plot-y-axis-symbolic-add.svg',
                validate_callback=self.validate_as_y)
            self._data_preview.preview_table().add_context_menu_action(
                'Show histogram for column',
                self.show_stats,
                'actions/view-plot-hist-symbolic-dark.svg',
                validate_callback=self.validate_as_hist)

        self.update_data(table_)

    def update_data(self, table_):
        if table_ is not None:
            self._data_preview.clear_filter()
            self._data_preview.show_decimals(4)
            self._table_model.set_table(table_)
            self.set_table_name(table_.get_name())
            self._attribute_model.set_attributes(
                self._table_model.table().get_table_attributes() or {})
            self._data_preview.set_row_column_legend(
                table_.number_of_rows(), table_.number_of_columns())
            self.jump_to_row_value.setRange(0, table_.number_of_rows())
        # Keep any old filter active
        self._data_preview.reapply_filter()
        if self.has_plot:
            self._plot.update_model(self._table_model)

    def set_model(self, model, transposed):
        if transposed:
            if isinstance(model, TransposedModel):
                model = model.base_model()
            else:
                model = TransposedModel(model)
        self._model = model
        self._data_preview.set_model(model, transposed)

    def set_table_name(self, name):
        if name is None:
            name = ''
        self._table_name_label.setText(name)
        self._table_name_label.setToolTip(name)

    def show_colors(self, show):
        self._legend.setVisible(show)
        self._table_model.set_show_colors(show)
        self._table_model.layoutChanged.emit()

    def _handle_jump_to_row(self):
        row = col = None
        if self._toggle_transpose_action.isChecked():
            col = self.jump_to_row_value.value()
        else:
            row = self.jump_to_row_value.value()
        self._data_preview.preview_table().center_on_cell(row, col)

    def show_none(self):
        if self.has_plot:
            self._plot.setVisible(False)

    def show_line(self):
        if self.has_plot:
            self._plot.setVisible(True)
            self._plot._on_show_line()

    def show_hist(self):
        if self.has_plot:
            self._plot.setVisible(True)
            self._plot._on_show_hist()

    def _handle_plot_type_changed(self, plot_type):
        if plot_type == PlotType.line:
            self._show_plot_button.setDefaultAction(self._show_line_action)
            self._plot.setVisible(True)
        elif plot_type == PlotType.hist:
            self._show_plot_button.setDefaultAction(self._show_hist_action)
            self._plot.setVisible(True)

    def _handle_toggle_transpose(self, transposed):
        old_selection = self._data_preview.preview_table().selection()
        attributes = self._toggle_attributes_action.isChecked()
        if attributes:
            model = self._attribute_model
        else:
            model = self._table_model
        self.set_model(model, transposed)

        # Reset selection
        if old_selection:
            selection_model = (
                self._data_preview.preview_table().selectionModel())
            old_minrow, old_maxrow, old_mincol, old_maxcol = old_selection

            start_index = self._model.index(old_mincol, old_minrow)
            end_index = self._model.index(old_maxcol - 1, old_maxrow - 1)
            item_selection = QtCore.QItemSelection(start_index, end_index)
            selection_model.select(
                item_selection, QtCore.QItemSelectionModel.Select)

    def _handle_toggle_attributes(self, attributes):
        if attributes:
            model = self._attribute_model
        else:
            model = self._table_model
        transposed = self._toggle_transpose_action.isChecked()
        self.set_model(model, transposed)

    def clear(self):
        self._table_model.set_table(table.File())
        self._attribute_model.set_attributes({})

    def copy_selection(self, row, column, include_headers=False):
        """
        Put selected values in the clipboard.
        Arguments row and column are not used. Feel free to refactor.
        """
        selection = self._data_preview.preview_table().selection()
        if selection is None:
            return

        self.copy_values(*selection, include_headers=include_headers)

    def copy_selection_with_column_names(self, row, column):
        """
        Put selected values including column names in the clipboard.
        Arguments row and column are not used. Feel free to refactor.
        """
        self.copy_selection(row, column, include_headers=True)

    def copy_column_name(self, row, column):
        """
        Put column name at in the clipboard.
        """
        if self._toggle_transpose_action.isChecked():
            self.copy_values(row, row + 1, 0, 0, include_headers=True)
        else:
            self.copy_values(0, 0, column, column + 1, include_headers=True)

    def copy_column_names(self, row, column):
        """
        Put all column names in the clipboard.
        Arguments row and column are not used. Feel free to refactor.
        """
        column_count = len(self._model.column_names())
        if self._toggle_transpose_action.isChecked():
            self.copy_values(0, column_count, 0, 0, include_headers=True)
        else:
            self.copy_values(0, 0, 0, column_count, include_headers=True)

    def copy_values(self, minrow, maxrow, mincol, maxcol,
                    include_headers=False):
        """
        Copy values from the currently shown model.
        Ranges minrow to maxrow and mincol to maxcol are half open; they
        include minrow/mincol but not maxrow/maxcol.
        If include_headers is True a row with the column names for the selected
        column will be included as the first row.
        """
        transposed = self._toggle_transpose_action.isChecked()
        headers = []
        values = []
        if maxrow - minrow == 0 and maxcol - mincol == 1 and include_headers:
            # Skip the html table when copying a single column name.
            if transposed:
                column_name = self._model.column_names()[minrow]
            else:
                column_name = self._model.column_names()[mincol]
            headers.append(column_name)
        elif (maxrow - minrow)*(maxcol - mincol) == 1 and not include_headers:
            # Skip the html table when copying a single value.
            qindex = self._model.index(minrow, mincol)
            values.append([str(self._model.data(
                qindex, role=QtCore.Qt.DisplayRole))])
        else:
            if include_headers and not transposed:
                headers = self._model.column_names()[mincol:maxcol]

            for row in range(minrow, maxrow):
                row_values = []
                if include_headers and transposed:
                    column_name = self._model.column_names()[row]
                    row_values.append(column_name)
                for col in range(mincol, maxcol):
                    qindex = self._model.index(row, col)
                    value = self._model.data(
                        qindex, role=QtCore.Qt.DisplayRole)
                    row_values.append(value)
                values.append(row_values)

        if headers and not values:
            # If copying _only_ headers, pass them as values instead.
            values, headers = [headers], None
        widget_utils.table_values_to_clipboard(values, headers=headers)

    def plot_as_x(self, row, column):
        column_name = self._model.column_name(row, column)
        self._plot.add_column_to_plot(column_name, as_y=False)

    def plot_as_y(self, row, column):
        column_name = self._model.column_name(row, column)
        self._plot.add_column_to_plot(column_name)

    def show_stats(self, row, column):
        column_name = self._model.column_name(row, column)
        self._plot.show_stats_for(column_name)

    def validate_as_x(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        try:
            column_name = self._model.column_name(row, column)
        except IndexError:
            return False
        col_dtype = self._model.table().column_type(column_name)
        if col_dtype.kind in VALID_AS_X:
            return True
        return False

    def validate_as_y(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        try:
            column_name = self._model.column_name(row, column)
        except IndexError:
            return False
        col_dtype = self._model.table().column_type(column_name)
        if col_dtype.kind in VALID_AS_Y:
            return True
        return False

    def validate_as_hist(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        try:
            column_name = self._model.column_name(row, column)
        except IndexError:
            return False
        col_dtype = self._model.table().column_type(column_name)
        if col_dtype.kind in VALID_AS_HIST:
            return True
        return False

    def validate_copy(self, row, column):
        if row < 0 or column < 0:
            return False
        return True

    def validate_copy_with_column_names(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        if row < 0 or column < 0:
            return False
        return True

    def validate_copy_column_names(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        if self._toggle_transpose_action.isChecked():
            row, column = column, row
        if row >= 0 or column < 0:
            return False
        return True

    def custom_menu_items(self):
        menu_items = []
        return menu_items


class Legend(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        groupbox = QtWidgets.QGroupBox('')

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        for row, text in enumerate(_typenames()):
            icon = ColorBoxLegend(COLUMN_COLORS[text], label=text[0])
            icon.setToolTip(text)
            # TODO: check old call, why pass row for alignment?
            # hlayout.addWidget(icon, 0, row)
            hlayout.addWidget(icon, 0)
        groupbox.setLayout(hlayout)
        layout.addStretch()
        layout.addWidget(groupbox)
        self.setLayout(layout)

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        text = self.toolTip()
        QtWidgets.QToolTip.showText(pos, text)
        super().mouseMoveEvent(event)


class ColorBoxLegend(QtWidgets.QWidget):
    def __init__(self, color, label=None, parent=None):
        super().__init__(parent)
        self.color = color
        self.setMinimumHeight(16)
        self.setMinimumWidth(16)
        self.setMaximumWidth(16)
        self.setMaximumHeight(16)

        self._label_str = label
        self._label = QtWidgets.QLabel('')
        self._label.setFont(self._get_font())
        self._label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        layout.addWidget(self._label)
        self.setLayout(layout)

        self.set_label(self._label_str)

    def set_label(self, label):
        if label is None:
            return
        self._label.setText(label)

    def _get_font(self):
        font = self._label.font()
        font.setItalic(True)
        return font

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), self.color)
        p.setPen(QtCore.Qt.black)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))


class PlotType(enum.Enum):
    hist = 0
    line = 1


class TableDataWrapper:
    """
    Workarounds for labels starting with _ being suppressed from the legend.
    These are replaced with kind of similar unicode double low line.

    Also handles index data.

    Finally, it has been designated to contain some functions to deal with
    unmasking arrays. The reason for this is that the cursors need the original
    datatypes in order to efficiently perform interpolation.
    """
    index_name = '(index)'
    _double_low_line = '\u2017'

    def __init__(self, table, x_name=None):
        self.set_x_name(x_name)
        self._table = table

    @staticmethod
    def unmask_arr(data):
        res = data
        if np.ma.is_masked(data):
            res = data.compressed()
        return res

    @staticmethod
    def unmask_xy(x_data, y_data):
        def maskarray(arr):
            if np.ma.is_masked(arr):
                return np.ma.getmaskarray(arr)

        x_mask = maskarray(x_data)
        y_mask = maskarray(y_data)

        # Unmask data removing values.
        if x_mask is not None and y_mask is not None:
            y_data[x_mask] = np.ma.masked
            x_data[y_mask] = np.ma.masked

            x_data = x_data.compressed()
            y_data = y_data.compressed()

        elif x_mask is not None:
            y_data = y_data[~x_mask]
            x_data = x_data.compressed()
        elif y_mask is not None:
            x_data = x_data[~y_mask]
            y_data = y_data.compressed()

        return x_data, y_data

    @classmethod
    def column_name(cls, name):
        if name is not None:
            return re.sub(cls._double_low_line, '^_', name)

    @classmethod
    def label_name(cls, name):
        if name:
            return re.sub('^_', cls._double_low_line, name)
        return name

    def __getitem__(self, signal):
        if self._x_name == self.index_name:
            x_data = np.arange(0, self._table.number_of_rows())
        else:
            x_data = self._table[self._x_name]
        y_data = self._table[self.column_name(signal)]
        x_data, y_data = self.unmask_xy(x_data, y_data)
        return (x_data, y_data)

    def set_x_name(self, x_name):
        x_name = self.column_name(x_name)
        self._x_name = x_name

    def set_table(self, table):
        self._table = table


class ViewerPlot(QtWidgets.QWidget):
    # plot_type_changed = QtCore.Signal(PlotType)
    # Declared signal as object to work around issue:
    #    https://bugreports.qt.io/browse/PYSIDE-239
    plot_type_changed = QtCore.Signal(object)

    def __init__(self, data_model=None, parent=None):
        super().__init__(parent)

        self._model = data_model
        self._x_model = QtGui.QStandardItemModel()
        self._y_model = QtGui.QStandardItemModel()
        self._hist_model = QtGui.QStandardItemModel()

        # show lines or histogram
        self._line_plot_active = True
        self._line_legend = None
        # _max_data_points defines the maximum number of data points before
        # we resample to data to short plot time
        self._max_data_points = 10000
        self._plot_style = 'both'

        # set the binning for the histogram
        self._binning_user_set = False

        self.setContentsMargins(1, 1, 1, 1)

        plot_toolbar = sywidgets.SyToolBar(self)

        self.x_label = QtWidgets.QLabel('X')
        self.x_value = QtWidgets.QComboBox()
        self.x_value.setMaximumWidth(100)
        self.x_value.setModel(self._x_model)
        self.x_value.setToolTip('Select the column used for the x values')
        self.y_label = QtWidgets.QLabel('Y')
        self.y_value = sywidgets.CheckableComboBox()
        self.y_value.setMaximumWidth(100)
        self.y_value.setModel(self._y_model)
        self.y_value.setToolTip('Select the columns used for the y values. '
                                'Multiple columns can be selected.')
        self.hist_label = QtWidgets.QLabel('Histogram')
        self.hist_label.setVisible(False)
        self.hist_value = QtWidgets.QComboBox()
        self.hist_value.setModel(self._hist_model)
        self.hist_value.setToolTip('Select the column to show histogram '
                                   'and statistics for.')
        self.hist_value.setVisible(False)

        resample_label = QtWidgets.QLabel('Resample')
        self.resample_value = QtWidgets.QSpinBox()
        self.resample_value.setMinimum(1)
        self.resample_value.setMaximum(100000)
        self.resample_value.setToolTip(
            'The step size is used to limit the number of values plotted, '
            'set automatically for large datasets.\n'
            '1: every value (no resampling), 2: every other value,  ... '
            'n: every nth value.')
        resample_widget = QtWidgets.QWidget(self)
        resample_widget.setContentsMargins(2, 2, 2, 2)
        resample_layout = QtWidgets.QHBoxLayout()
        resample_layout.setContentsMargins(0, 0, 0, 0)
        resample_layout.addWidget(resample_label)
        resample_layout.addWidget(self.resample_value)
        resample_widget.setLayout(resample_layout)

        binning_label = QtWidgets.QLabel('Binning')
        self.binning_value = QtWidgets.QSpinBox()
        self.binning_value.setValue(10)
        self.binning_value.setMinimum(1)
        self.binning_value.setMaximum(100000)
        self.binning_value.setToolTip('The number of bins used '
                                      'for the histogram.')
        binning_widget = QtWidgets.QWidget(self)

        binning_widget.setContentsMargins(2, 2, 2, 2)
        binning_layout = QtWidgets.QHBoxLayout()
        binning_layout.setContentsMargins(0, 0, 0, 0)
        binning_layout.addWidget(binning_label)
        binning_layout.addWidget(self.binning_value)
        binning_widget.setLayout(binning_layout)

        self._style_both_action = sywidgets.create_action(
            text='Line and marker',
            icon_name='actions/plot-style-line-and-marker.svg',
            tooltip_text='Line and markers',
            triggered=self.set_style_both)
        self._style_line_action = sywidgets.create_action(
            text='Line',
            icon_name='actions/plot-style-line.svg',
            tooltip_text='Line',
            triggered=self.set_style_line)
        self._style_marker_action = sywidgets.create_action(
            text='Marker',
            icon_name='actions/plot-style-marker.svg',
            tooltip_text='Markers',
            triggered=self.set_style_marker)
        self._plot_style_button = sywidgets.MenuToolButton(
            self._style_both_action, [
                self._style_both_action,
                self._style_line_action,
                self._style_marker_action])

        self._hist_label_action = plot_toolbar.addWidget(self.hist_label)
        self._hist_value_action = plot_toolbar.addWidget(self.hist_value)
        self._x_label_action = plot_toolbar.addWidget(self.x_label)
        self._x_value_action = plot_toolbar.addWidget(self.x_value)
        self._y_label_action = plot_toolbar.addWidget(self.y_label)
        self._y_value_action = plot_toolbar.addWidget(self.y_value)
        plot_toolbar.addSeparator()
        self.binning_action = plot_toolbar.addWidget(binning_widget)
        self.binning_action.setVisible(False)
        self.resample_action = plot_toolbar.addWidget(resample_widget)
        self._plot_style_action = plot_toolbar.addWidget(self._plot_style_button)
        self._export_action = plot_toolbar.add_action(
            "Export selected",
            icon_name="actions/export-selected-plot-points.svg",
            triggered=self._export_csv,
            tooltip_text="Export plotted points between cursors to csv")

        self._cursor_button = CursorWidgetToolButton(plot_toolbar)
        self._cursor_button_action = plot_toolbar.addWidget(
            self._cursor_button)

        # figure
        self.figure = _matplotlib().figure.Figure()
        self._set_figure_background_color()
        self.canvas = _matplotlib().backends.backend_qt5agg.FigureCanvasQTAgg(
            self.figure)
        frame = QtWidgets.QFrame()
        frame.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        frame_layout = QtWidgets.QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame_layout)
        frame_layout.addWidget(self.canvas)
        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setVerticalStretch(1)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.canvas.setSizePolicy(policy)
        self.canvas.setMinimumWidth(300)
        self.axes = self.figure.add_subplot(111)

        # Cursor

        grabber = _widget_mpl().Grabber()
        self._cursors_enabled = False
        self._n_cursors = 0
        self._cursor_stats = False
        self._cursor_delta = False
        self._snapper = _widget_mpl().Snapper([], [])
        self._data_wrapper = TableDataWrapper(self._model.table())

        self._cursors = _widget_mpl().VerticalCursorController(
            self.axes, self._snapper, grabber, [], self._data_wrapper)
        self._cursor_model = _widget_mpl().CursorTableModel(
            self._cursors, [])
        self._cursor_table = QtWidgets.QTableView()
        self._cursor_table.setModel(self._cursor_model)
        cursor_delegate = _widget_mpl().CursorTableItemDelegate()
        self._cursor_table.setItemDelegate(cursor_delegate)
        self._cursor_table.setVisible(False)

        # Default navigation toolbar for matplotlib
        self.mpl_toolbar = sywidgets.mpl_toolbar_factory(self.canvas, self)

        # Figure Layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(plot_toolbar)
        layout.addWidget(frame)
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self._cursor_table)

        self.setLayout(layout)

        self._update_signal_comboboxes()

        self._timeout_after = 500
        self._update_plot_timer = QtCore.QTimer(self)
        self._update_plot_timer.setInterval(self._timeout_after)
        self._update_plot_timer.setSingleShot(True)

        self.hist_value.currentIndexChanged[int].connect(
            self._plot_selection_changed)
        self.x_value.currentIndexChanged[int].connect(
            self._plot_selection_changed)
        self.y_value.currentIndexChanged[int].connect(
            self._plot_selection_changed)
        self.y_value.selectedItemsChanged.connect(
            self._update_plot_timer.start)
        self.resample_value.valueChanged[int].connect(
            self._resample_value_changed)
        self.binning_value.valueChanged.connect(self._binning_value_changed)
        self._update_plot_timer.timeout.connect(self._update_plot)

        self._cursor_button.n_cursors_changed.connect(
            self._handle_n_cursors_changed)
        self._cursor_button.show_stats_toggled.connect(
            self._handle_stats_toggled)
        self._cursor_button.show_delta_toggled.connect(
            self._handle_delta_toggled)
        self._cursor_button.snap_toggled.connect(
            self._handle_snap_toggled)
        self._cursor_button.toggled.connect(self._handle_cursor_toggled)
        self.setMinimumWidth(500)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._draw_canvas()

    def _set_figure_background_color(self):
        # FIXME: setting the correct facecolor for matplotlib figures embedded
        # in QTabWidgets doesn't work
        color = self.palette().color(self.backgroundRole())
        self.figure.set_facecolor(color.name())

    def _draw_canvas(self):
        self.axes.relim()
        self.axes.autoscale_view(True, True, True)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _handle_cursor_toggled(self, enabled):
        self._cursors_enabled = enabled
        self._update_plot_timer.start()
        self._cursor_table.setVisible(enabled)

    def _handle_n_cursors_changed(self, n):
        self._n_cursors = n
        self._update_plot_timer.start()

    def _handle_stats_toggled(self, stats):
        self._cursor_stats = stats
        self._update_plot_timer.start()

    def _handle_snap_toggled(self, snap):
        self._cursors.set_snap(snap)

    def _handle_delta_toggled(self, delta):
        self._cursor_delta = delta
        self._update_plot_timer.start()

    def set_style_both(self):
        self._plot_style = 'both'
        self._update_plot()

    def set_style_line(self):
        self._plot_style = 'line'
        self._update_plot()

    def set_style_marker(self):
        self._plot_style = 'marker'
        self._update_plot()

    def _update_plot(self, redraw=True):
        table = self._model.table()
        if table is None:
            return
        if self._line_legend is not None:
            old_legend_loc = self._line_legend._loc
        else:
            old_legend_loc = 1
        self.axes.cla()  # clear plot
        self._cursor_model.clear_columns()

        # show line plots
        if self._line_plot_active:
            x_column_name = self.x_value.currentText()
            y_column_names = self.y_value.checkedItemNames()
            self._data_wrapper.set_x_name(x_column_name)

            for y_column_name in y_column_names:
                self._plot_line(x_column_name, y_column_name)
            if len(y_column_names) == 1:
                y_attr = table.get_column_attributes(y_column_names[0])
                unit = y_attr.get('unit', None)
                y_label = str(y_column_names[0])
                if unit is not None:
                    y_label += ' [{}]'.format(unit)
                self.axes.set_ylabel(y_label)

            lines = [l for l in self.axes.lines]

            if len(lines):
                labels = [l.get_label() for l in lines]
                new_labels = [TableDataWrapper.label_name(l.get_label())
                              for l in lines]

                if self._cursors_enabled:
                    # restore cursors
                    self._cursor_model.clear_columns()
                    for label in labels:
                        self._cursor_model.insert_column(label)

                    if x_column_name == self._plot_x_column_name:
                        self._cursors.add()
                    else:
                        # Reset cursor config when switching x-axis.
                        self._cursor_model.set_n_cursors(0)
                    self._cursor_model.set_n_cursors(self._n_cursors)
                    self._cursor_model.set_show_delta(self._cursor_delta)
                    self._cursor_model.set_show_stats(self._cursor_stats)

                self._line_legend = self.axes.legend(
                    lines, new_labels, loc='upper left')
            else:
                self._line_legend = None

            if self._line_legend is not None:
                try:
                    self._line_legend.set_draggable(True, use_blit=True)
                except AttributeError:
                    # Assume use of older version.
                    self._line_legend.draggable(True, use_blit=True)

                # (Bene) not a good way to use private variables
                self._line_legend._loc = old_legend_loc

            self._plot_x_column_name = x_column_name
        else:
            # show histogram
            hist_column = self.hist_value.currentText()
            if hist_column:
                self._plot_hist(hist_column)
        if redraw:
            self._draw_canvas()

    def _plot_hist(self, y_column_name):
        table = self._model.table()
        row_slice = slice(0,
                          table.number_of_rows(),
                          int(self.resample_value.value()))
        y_data = table.get_column_to_array(y_column_name)[row_slice]
        y_dtype = table.column_type(y_column_name)
        text_params = collections.OrderedDict()

        if isinstance(y_data, np.ma.MaskedArray):
            # Count masked values, but never plot them.
            masked = np.count_nonzero(y_data.mask)
            y_data = y_data.compressed()
        else:
            masked = 0

        if y_dtype.kind in ['S', 'U', 'b']:
            # These data type can not be placed on a continuous axis.
            all_bin_labels, full_hist = np.unique(y_data, return_counts=True)
            if not self._binning_user_set:
                # 10 is the maximum number of bins for automatic binning
                bin_count = min(10, len(full_hist))
            else:
                bin_count = self.binning_value.value()

            # Sort and slice histogram
            hist = full_hist
            bin_labels = all_bin_labels
            if y_dtype.kind == 'b':
                # Always sort True before False
                if all_bin_labels[0] == False:
                    hist = full_hist[::-1]
                    bin_labels = all_bin_labels[::-1].astype(str)
            else:
                # Sort other types by number of occurances
                sorted_ = sorted(zip(full_hist, all_bin_labels),
                                 key=operator.itemgetter(0), reverse=True)
                hist, bin_labels = zip(*sorted_[:bin_count])
                other = sum(h[0] for h in sorted_[bin_count:])
                if other > 0:
                    hist = list(hist) + [other]
                    bin_labels = list(bin_labels) + ["<other>"]

            self.axes.bar(bin_labels, hist)
            text_params['unique values'] = len(full_hist)
        elif y_dtype.kind in ['f', 'i', 'u', 'M']:
            # These data type can be placed on a continuous axis.
            if not self._binning_user_set:
                # 10 is the maximum number of bins for automatic binning
                bin_count = min(10, int(np.sqrt(len(y_data))))
            else:
                bin_count = self.binning_value.value()

            nan_count = None
            if y_dtype.kind == 'M':
                y_data = _matplotlib().dates.date2num(y_data.tolist())
            elif y_dtype.kind == 'f':
                nans = np.isnan(y_data)
                nan_count = np.count_nonzero(nans)
                y_data = y_data[np.logical_not(nans)]

            if len(y_data):
                hist, bins = np.histogram(y_data, bin_count)
                width = bins[1] - bins[0]
                self.axes.bar(bins[:-1], hist, width=width, align='edge')
                if y_dtype.kind == 'M':
                    locator = _matplotlib().dates.AutoDateLocator()
                    self.axes.xaxis.set_major_locator(locator)
                    self.axes.xaxis.set_major_formatter(
                        _matplotlib().dates.AutoDateFormatter(locator))

            if not len(y_data):
                text_params['mean'] = '--'
                text_params['std'] = '--'
            elif y_dtype.kind == 'M':
                text_params['mean'] = str(
                    _matplotlib().dates.num2date(np.mean(y_data)))
                text_params['std'] = str(
                    datetime.timedelta(days=np.std(y_data)))
            else:
                text_params['mean'] = '{:.3g}'.format(np.nanmean(y_data))
                text_params['std'] = '{:.3g}'.format(np.nanstd(y_data))
            if y_dtype.kind == 'f':
                text_params['nan'] = nan_count

        text_params['masked'] = masked
        text = "\n".join(["{}: {}".format(k, v)
                          for k, v in text_params.items()])
        # TODO: make the textbox draggable like the legend in line plot
        text_box = _matplotlib().offsetbox.TextArea(text)
        anchored_offset_box = _matplotlib().offsetbox.AnchoredOffsetbox(
            loc=1, child=text_box)
        self.axes.add_artist(anchored_offset_box)

    def _plot_line(self, x_column_name, y_column_name):
        def get_plot_style_kwargs():
            plot_kwargs = {}
            if self._plot_style in ['marker', 'both']:
                plot_kwargs['marker'] = '.'
            else:
                plot_kwargs['marker'] = ' '
            if self._plot_style in ['line', 'both']:
                plot_kwargs['linestyle'] = 'solid'
            else:
                plot_kwargs['linestyle'] = ' '
            return plot_kwargs

        table = self._model.table()
        column_names = table.column_names()
        resample_value = int(self.resample_value.value())
        row_slice = slice(0,
                          table.number_of_rows(),
                          resample_value)
        y_data = table.get_column_to_array(y_column_name)[row_slice]
        y_dtype = table.column_type(y_column_name)
        if x_column_name in column_names:
            x_data = table.get_column_to_array(x_column_name)[row_slice]
            x_dtype = table.column_type(x_column_name)
            x_attr = table.get_column_attributes(x_column_name)
        else:
            x_data = np.arange(0, table.number_of_rows(), resample_value)
            x_dtype = x_data.dtype
            x_attr = {}

        x_data, y_data = TableDataWrapper.unmask_xy(x_data, y_data)

        if len(x_data) == len(y_data):
            xdate = x_dtype.kind == 'M'
            ydate = y_dtype.kind == 'M'
            plot_kwargs = get_plot_style_kwargs()
            if xdate or ydate:
                if xdate:
                    x_data = x_data.astype(datetime.datetime)
                if ydate:
                    y_data = y_data.astype(datetime.datetime)

                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    # Ignore harmless UserWarning about redundant marker which
                    # happens because fmt='o' in plot_date, kwargs marker will
                    # override it.
                    self.axes.plot_date(x_data, y_data, label=y_column_name,
                                        xdate=xdate, ydate=ydate, **plot_kwargs)
                if xdate:
                    self.axes.get_figure().autofmt_xdate()
            else:
                self.axes.plot(x_data, y_data, label=y_column_name, **plot_kwargs)
            unit = x_attr.get('unit', None)
            x_label = str(x_column_name)
            if unit is not None:
                x_label += ' [{}]'.format(unit)
            self.axes.set_xlabel(x_label)

        if x_data is not None:
            self._snapper.set_xdata(
                np.sort(TableDataWrapper.unmask_arr(x_data)))

    def _get_data_between_cursors(self):
        interval = None
        if self._n_cursors == 2:
            interval = self._cursors.interval()

        labels = self._cursors.data_line_labels()
        row_data = []
        column_names = [TableDataWrapper.column_name(label)
                        for label in labels]
        if labels:
            if interval:
                xdata = self._cursors.interval_line_data(labels[0])[0]
                ydatas = [self._cursors.interval_line_data(label)[1]
                          for label in labels]
            else:
                xdata = self._cursors.line_data(labels[0])[0]
                ydatas = [self._cursors.line_data(label)[1]
                          for label in labels]

            column_names.insert(0, self._plot_x_column_name)
            row_data = list(zip(*[xdata] + ydatas))

        return column_names, row_data

    def _export_csv(self):
        default_filename = os.path.join(
            settings.get_default_dir(), 'Plot data.csv')
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select file", default_filename,
            filter="CSV files (*.csv)")
        if filename:
            column_names, rows = self._get_data_between_cursors()
            table.File._rows_to_csv(filename, rows, column_names)

    def _plot_selection_changed(self, idx):
        self._update_plot_timer.start()

    def _resample_value_changed(self, idx):
        self._update_plot_timer.start()

    def _binning_value_changed(self, idx):
        self._binning_user_set = True
        self._update_plot_timer.start()

    def _update_hist_combobox(self):
        column_names = self._model.column_names()
        table = self._model.table()
        column_names = [name for name in column_names
                        if table.column_type(name).kind in VALID_AS_HIST]
        current_selection = self.hist_value.currentText()
        self.hist_value.clear()
        self.hist_value.addItems(column_names)
        idx = 0
        if current_selection in column_names:
            idx = column_names.index(current_selection)
        self.hist_value.setCurrentIndex(idx)

    def _update_x_combobox(self):
        column_names = self._model.column_names()
        table = self._model.table()
        column_names = [name for name in column_names
                        if table.column_type(name).kind in VALID_AS_X]
        column_names = [TableDataWrapper.index_name] + column_names
        current_selection = self.x_value.currentText()
        self.x_value.clear()
        self.x_value.addItems(column_names)
        idx = 0
        if current_selection in column_names:
            idx = column_names.index(current_selection)
        self.x_value.setCurrentIndex(idx)

    def _update_y_combobox(self):
        column_names = self._model.column_names()
        table = self._model.table()
        column_names = [name for name in column_names
                        if table.column_type(name).kind in VALID_AS_Y]
        current_selection = self.y_value.checkedItemNames()
        current_text = self.y_value.currentText()
        self.y_value.clear()
        for name in column_names:
            checked = name in current_selection
            self.y_value.add_item(name, checked)
        idx = 0
        if current_text in column_names:
            idx = column_names.index(current_text)
        self.y_value.setCurrentIndex(idx)

    def _update_signal_comboboxes(self):
        self._update_hist_combobox()
        self._update_x_combobox()
        self._update_y_combobox()

    def _on_show_line(self):
        self.plot_type_changed.emit(PlotType.line)
        self._hist_label_action.setVisible(False)
        self._hist_value_action.setVisible(False)
        self.binning_action.setVisible(False)
        self._x_label_action.setVisible(True)
        self._x_value_action.setVisible(True)
        self._y_label_action.setVisible(True)
        self._y_value_action.setVisible(True)
        self.resample_action.setVisible(True)
        self._plot_style_action.setVisible(True)
        self._export_action.setVisible(True)
        # self._cursor_button.setVisible(True)
        self._cursor_button_action.setVisible(True)
        self._cursor_table.setVisible(self._cursors_enabled)
        self._line_plot_active = True
        self._update_plot()

    def _on_show_hist(self):
        self.plot_type_changed.emit(PlotType.hist)
        self._hist_label_action.setVisible(True)
        self._hist_value_action.setVisible(True)
        self.binning_action.setVisible(True)
        self._x_label_action.setVisible(False)
        self._x_value_action.setVisible(False)
        self._y_label_action.setVisible(False)
        self._y_value_action.setVisible(False)
        self.resample_action.setVisible(True)
        self._plot_style_action.setVisible(False)
        self._export_action.setVisible(False)
        # self._cursor_button.setEnabled(False)
        self._cursor_button_action.setVisible(False)
        self._cursor_table.setVisible(False)
        self._line_plot_active = False
        self._update_plot()

    def add_column_to_plot(self, column_name, as_y=True):
        if as_y:
            items = self._y_model.findItems(column_name)
            if len(items):
                idx = items[0].row()
                self.y_value.set_checked_state(idx, True)
            else:
                idx = -1
            self.y_value.setCurrentIndex(idx)
        else:
            items = self._x_model.findItems(column_name)
            if len(items):
                idx = items[0].row()
            else:
                idx = -1
            self.x_value.setCurrentIndex(idx)
        self._on_show_line()

    def show_stats_for(self, column_name):
        items = self._hist_model.findItems(column_name)
        if len(items):
            column_idx = items[0].row()
        else:
            column_idx = -1
        self.hist_value.setCurrentIndex(column_idx)
        self._on_show_hist()

    def set_max_data_points(self, value):
        self._max_data_points = int(value)

    def get_cursor_model(self):
        return self._cursor_model

    def update_model(self, model):
        self._model = model
        table = self._model.table()

        self._data_wrapper.set_table(table)
        self._data_wrapper.set_x_name(self.x_value.currentText())

        col_names = []
        if table:
            col_names = table.column_names()

        self._cursor_model.set_col_headers(col_names)
        # compute a staring value for re-sampling so the
        # number of points per line is not above self._max_data_points
        rows = self._model.rowCount(None)
        if rows > self._max_data_points:
            start_resample_value = int(round(rows / self._max_data_points))
            self.resample_value.setValue(start_resample_value)
        else:
            self.resample_value.setValue(1)
        self._update_signal_comboboxes()
        self._update_plot()
