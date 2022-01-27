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
"""
Created on Mon Nov 05 08:23:41 2012

@author: Helena
"""
import re
import os
import sys
import html
from sympathy.api import importers
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api import qt2 as qt_compat
from sympathy.api import datasource
from sympathy.utils import credentials
from sympathy.api import exceptions
from sylib import url
from sylib import odbc
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')
sql = table.table_sql()
QueryError = sql.QueryError


def _build_where_query(tables, columns, join_columns, where_conditions):
    """Return a SQL query from input arguments using WHERE."""
    query = 'SELECT '
    query += ', '.join(columns)
    query += ' FROM '
    query += ', '.join(tables)
    if join_columns or where_conditions:
        query += ' WHERE '
    joins = []

    if join_columns:
        for ind in range(1, len(join_columns), 2):
            joins.append(join_columns[ind - 1] + '=' + join_columns[ind])
        query += ' AND '.join(joins)
    if where_conditions:
        if join_columns:
            query += ' AND '
        query += ' AND '.join(where_conditions)

    return query


_file_mode = datasource.File.modes.file
_sqlalchemy_mode = datasource.File.modes.db_sqlalchemy
_odbc_mode = datasource.File.modes.db
_db_modes = [_sqlalchemy_mode, _odbc_mode]


def _expand_login(mode):
    login_modes = {
        _odbc_mode: odbc.expand_login,
        _sqlalchemy_mode: url.expand_login,
    }
    return login_modes.get(mode, None)


class DataImportSQLWidget(QtWidgets.QWidget):
    def __init__(self, parameters, node, data, db_interface_factory):
        super().__init__()
        self._parameters = parameters
        self._db_interface_factory = db_interface_factory
        self._data = data
        resource = self._data.decode_path()
        if self._data.decode_type() in _db_modes:
            try:
                credentials.get_credentials_async(
                    node, self._data.connection(),
                    self._async_init_db_interface)
            except exceptions.SyCredentialError:
                self._init_db_interface(None)
        else:
            self._init_db_interface(resource)

    def _async_init_db_interface(self, secrets):
        try:
            credentials.validate_credentials(self._data.connection(), secrets)
        except Exception:
            secrets = credentials.fill_secrets(
                self._data.connection(), secrets)

        resource = credentials.expand_credentials(
            self._data.connection(), secrets, _expand_login(
                self._data.decode_type()))
        self._init_db_interface(resource)

    def _init_db_interface(self, resource):
        self._db_interface = self._db_interface_factory(resource)

        self._init_parameters()
        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        hlayout_simple_table = QtWidgets.QHBoxLayout()
        hlayout_query_edit = QtWidgets.QHBoxLayout()
        hlayout_join_info = QtWidgets.QHBoxLayout()
        hlayout_where = QtWidgets.QHBoxLayout()
        max_height = 150

        if isinstance(self._db_interface, sql.ODBCDatabase):
            vlayout.addWidget(self._parameters['odbc'].gui())
        # Create ButtonGroup
        self._sqlite_query_alternatives = QtWidgets.QButtonGroup()
        self._sqlite_query_alternatives.setExclusive(True)

        self._table_query_button = QtWidgets.QRadioButton('Table query')
        self._table_query_button.setChecked(True)
        self._lineedit_query_button = QtWidgets.QRadioButton('Write query')
        self._custom_query_button = QtWidgets.QRadioButton('Make custom query')
        # Add buttons to group
        self._sqlite_query_alternatives.addButton(self._table_query_button)
        self._sqlite_query_alternatives.addButton(self._lineedit_query_button)
        self._sqlite_query_alternatives.addButton(self._custom_query_button)
        # Add group to layout

        status_label = QtWidgets.QLabel()
        vlayout.addWidget(status_label)
        vlayout.addWidget(self._table_query_button)

        self._table_name_label = QtWidgets.QLabel("Choose table.")
        self._table_name_combo = QtWidgets.QComboBox()
        hlayout_simple_table.addWidget(self._table_name_label)
        hlayout_simple_table.addWidget(self._table_name_combo)
        vlayout.addLayout(hlayout_simple_table)
        vlayout.addWidget(self._lineedit_query_button)
        self._query_label = QtWidgets.QLabel("SQL query:")
        self._query_edit = QtWidgets.QLineEdit(self)
        hlayout_query_edit.addWidget(self._query_label)
        hlayout_query_edit.addWidget(self._query_edit)
        vlayout.addLayout(hlayout_query_edit)
        vlayout.addWidget(self._custom_query_button)
        self._join_tables = QtWidgets.QListWidget()
        self._join_tables.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)
        self._join_tables.setMaximumHeight(max_height)

        table_names = []
        fail_status = ''

        if self._db_interface.is_null():
            fail_status = 'Error: could not connect to database'

        if not fail_status:
            try:
                table_names = self._db_interface.table_names()
            except Exception:
                fail_status = 'Error: could not get table names from database'

        if fail_status:
            status_label.setText(html.escape(fail_status))
        else:
            status_label.setVisible(False)

        table_name = self._parameters["table_names"].selected
        ext_table_names = table_names
        if table_name and table_name not in table_names:
            ext_table_names = ([table_name] + table_names)
        self._parameters['table_names'].list = ext_table_names

        self._join_tables.addItems(table_names)
        self._table_columns = QtWidgets.QListWidget()
        self._table_columns.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)
        self._table_columns.setMaximumHeight(max_height)
        self._label_join_tables = QtWidgets.QLabel("Select tables")
        vlayout_join_tables = QtWidgets.QVBoxLayout()
        vlayout_join_tables.addWidget(self._label_join_tables)
        vlayout_join_tables.addWidget(self._join_tables)
        hlayout_join_info.addLayout(vlayout_join_tables)
        self._label_table_columns = QtWidgets.QLabel(
            "Select resulting table columns")
        vlayout_table_columns = QtWidgets.QVBoxLayout()
        vlayout_table_columns.addWidget(self._label_table_columns)
        vlayout_table_columns.addWidget(self._table_columns)
        hlayout_join_info.addLayout(vlayout_table_columns)

        self._join_column_selection = QtWidgets.QListWidget()
        self._join_column_selection.setDragEnabled(True)
        self._join_column_selection.setMaximumHeight(max_height)
        self._label_join_column_selection = QtWidgets.QLabel(
            "Double click on names to add to join")
        # vlayout_join_column_selection = QtWidgets.QVBoxLayout()
        # vlayout_join_column_selection.addWidget(
        #     self._label_join_column_selection)
        # vlayout_join_column_selection.addWidget(self._join_column_selection)
        # hlayout_join_info.addLayout(vlayout_join_column_selection)

        hlayout_where_preview = QtWidgets.QHBoxLayout()
        self._join_columns = QtWidgets.QListWidget()
        # Added for double click method
        self._join_columns.setDragDropMode(
            QtWidgets.QAbstractItemView.InternalMove)
        self._join_columns.setAcceptDrops(True)
        self._join_columns.setDropIndicatorShown(True)
        self._join_columns.setMaximumHeight(max_height)
        self._label_join_columns = QtWidgets.QLabel(
            "Join on two consecutive column names. Double click to remove."
            "Change order by drag and drop.")
        self._label_join_columns.setWordWrap(True)
        # vlayout_join_columns = QtWidgets.QVBoxLayout()
        # vlayout_join_columns.addWidget(
        #     self._label_join_columns)
        # vlayout_join_columns.addWidget(self._join_columns)
        # hlayout_join_info.addLayout(vlayout_join_columns)

        # For adding where statements
        hlayout_where_combo = QtWidgets.QHBoxLayout()
        self._where_column_combo = QtWidgets.QComboBox()
        hlayout_where_combo.addWidget(self._where_column_combo)
        self._where_comparison = QtWidgets.QComboBox()
        hlayout_where.addWidget(self._where_comparison)
        self._where_condition = QtWidgets.QLineEdit()
        hlayout_where.addWidget(self._where_condition)
        self._where_add_button = QtWidgets.QPushButton('Add', self)
        hlayout_where.addWidget(self._where_add_button)
        self._where_condition_list = QtWidgets.QListWidget()
        self._where_condition_list.setDragDropMode(
            QtWidgets.QAbstractItemView.InternalMove)
        self._where_condition_list.setAcceptDrops(True)
        self._where_condition_list.setDropIndicatorShown(True)
        self._where_condition_list.setMaximumHeight(max_height)
        self._label_where_condition = QtWidgets.QLabel(
            "Add WHERE statements")
        self._label_where_condition.setWordWrap(True)
        vlayout_where_condition = QtWidgets.QVBoxLayout()
        vlayout_where_condition.addWidget(
            self._label_where_condition)
        vlayout_where_condition.addLayout(hlayout_where_combo)
        vlayout_where_condition.addLayout(hlayout_where)
        vlayout_where_condition.addWidget(self._where_condition_list)
        hlayout_where_preview.addLayout(vlayout_where_condition)

        # Preview buttons, tables and label created.
        self._preview_query_button = QtWidgets.QPushButton('Preview query')
        self._preview_query_button.setFixedWidth(150)
        self._preview_query = QtWidgets.QLabel('Query')
        self._preview_query.setWordWrap(True)
        hlayout_query_preview = QtWidgets.QHBoxLayout()
        hlayout_query_preview.addWidget(self._preview_query_button)
        hlayout_query_preview.addWidget(self._preview_query)

        self._preview_table_button = QtWidgets.QPushButton('Preview table')
        self._preview_table = QtWidgets.QTableWidget()
        self._preview_table.setMaximumHeight(max_height)
        vlayout_table_preview = QtWidgets.QVBoxLayout()
        vlayout_table_preview.addWidget(self._preview_table_button)
        vlayout_table_preview.addWidget(self._preview_table)

        hlayout_where_preview.addLayout(vlayout_table_preview)

        vlayout.addLayout(hlayout_join_info)
        vlayout.addLayout(hlayout_where_preview)
        vlayout.addLayout(hlayout_query_preview)
        self.setLayout(vlayout)

        table_name = self._parameters["table_names"].selected
        self._table_name_combo.addItems(ext_table_names)
        if table_name:
            if table_name in ext_table_names:
                self._table_name_combo.setCurrentIndex(
                    ext_table_names.index(table_name))
        else:
            self._table_name_combo.setCurrentIndex(-1)
        self._query_edit.setText(self._parameters["query_str"].value)

        self._table_query_button.setChecked(
            self._parameters["table_query"].value)
        self._table_query_enable(self._parameters["table_query"].value)
        self._lineedit_query_button.setChecked(
            self._parameters["lineedit_query"].value)
        self._lineedit_query_enable(self._parameters["lineedit_query"].value)
        self._custom_query_button.setChecked(
            self._parameters["custom_query"].value)
        self._custom_query_enable(self._parameters["custom_query"].value)

        for item in self._parameters["join_tables"].list:
            try:
                self._join_tables.findItems(
                    item, QtCore.Qt.MatchCaseSensitive)[0].setSelected(True)
            except IndexError:
                pass

        # Add column names and mark previous selected ones as selected
        self._names_changed()

        for item in self._parameters["table_columns"].list:
            try:
                self._table_columns.findItems(
                    item, QtCore.Qt.MatchCaseSensitive)[0].setSelected(
                        True)
            except IndexError:
                pass

        for item in self._parameters["join_column_selection"].list:
            try:
                self._join_column_selection.findItems(
                    item, QtCore.Qt.MatchCaseSensitive)[0].setSelected(True)
            except IndexError:
                pass

        # Init where combos
        self._where_column_combo.clear()
        self._where_column_combo.addItems(
            self._parameters["where_column_combo"].list)
        if self._parameters["where_column_combo"].list:
            self._where_column_combo.setCurrentIndex(
                self._parameters["where_column_combo"].value[0])
        self._where_comparison.addItems(
            self._parameters["where_comparison_combo"].list)
        if self._parameters["where_comparison_combo"].list:
            self._where_comparison.setCurrentIndex(
                self._parameters["where_comparison_combo"].value[0])
        self._where_condition.setText(
            self._parameters["where_condition"].value)
        self._where_condition_list.clear()
        self._where_condition_list.addItems(
            self._parameters["where_condition_list"].list)

        self._table_name_combo.currentIndexChanged[int].connect(self._row_changed)
        self._query_edit.textChanged[str].connect(self._query_changed)

        self._join_tables.itemClicked.connect(self._names_changed)
        self._table_columns.itemClicked.connect(self._columns_changed)
        self._join_tables.itemSelectionChanged.connect(self._names_changed)
        self._table_columns.itemSelectionChanged.connect(
            self._columns_changed)

        # For double click method
        self._join_column_selection.itemDoubleClicked.connect(
            self._add_double_click)
        self._join_columns.itemDoubleClicked.connect(self._remove_double_click)
        self._join_columns.itemClicked.connect(self._change_order)
        self._join_columns.currentRowChanged.connect(self._change_order)

        self._where_condition_list.itemDoubleClicked.connect(
            self._remove_where_condition)
        self._where_condition_list.currentRowChanged.connect(
            self._change_order_where)

        # For where combo boxes changed
        (self._where_column_combo.currentIndexChanged[int].
            connect(self._where_column_changed))
        (self._where_comparison.currentIndexChanged[int].
            connect(self._where_comparison_changed))
        (self._where_condition.textChanged[str].
            connect(self._where_condition_changed))
        # Button clicked, add where statement
        self._where_add_button.clicked.connect(self._add_where_clause)

        # Preview buttons clicked:
        self._preview_table_button.clicked.connect(self._add_preview_table)
        self._preview_query_button.clicked.connect(self._add_preview_query)

        # query selection radiobuttons clicked
        self._table_query_button.clicked.connect(
            self._table_query_button_clicked)

        self._lineedit_query_button.clicked.connect(
            self._lineedit_query_button_clicked)

        self._custom_query_button.clicked.connect(
            self._custom_query_button_clicked)

    def _init_parameters(self):
        try:
            self._parameters["table_query"]
        except KeyError:
            self._parameters.set_boolean("table_query", value=True)
        try:
            self._parameters["table_names"]
        except KeyError:
            self._parameters.set_list(
                "table_names", [], value=[0])
        try:
            self._parameters["query_str"]
        except KeyError:
            self._parameters.set_string("query_str")
        try:
            self._parameters["lineedit_query"]
        except KeyError:
            self._parameters.set_boolean("lineedit_query", value=False)
        try:
            self._parameters["custom_query"]
        except KeyError:
            self._parameters.set_boolean("custom_query", value=False)
        try:
            self._parameters["join_tables"]
        except KeyError:
            self._parameters.set_list("join_tables")
        try:
            self._parameters["table_columns"]
        except KeyError:
            self._parameters.set_list("table_columns")
        try:
            self._parameters["join_column_selection"]
        except KeyError:
            self._parameters.set_list("join_column_selection")
        try:
            self._parameters["join_columns"]
        except KeyError:
            self._parameters.set_list("join_columns")
        try:
            self._parameters["where_add_comparison"]
        except KeyError:
            self._parameters.set_string("where_add_comparison")
        try:
            self._parameters["where_column_combo"]
        except KeyError:
            self._parameters.set_list("where_column_combo",
                                      self._parameters['join_column_selection']
                                      .list)
        try:
            self._parameters["where_comparison_combo"]
        except KeyError:
            self._parameters.set_list("where_comparison_combo",
                                      ['=', '<', '>', '>=', '<=', '!=',
                                       ' LIKE ', ' GLOB ', ' BETWEEN '])
        try:
            self._parameters["where_condition"]
        except KeyError:
            self._parameters.set_string("where_condition")
        try:
            self._parameters["where_condition_list"]
        except KeyError:
            self._parameters.set_list("where_condition_list")
        try:
            self._parameters["preview_query"]
        except KeyError:
            self._parameters.set_string("preview_query")

        try:
            self._parameters['odbc']
        except KeyError:
            self._parameters.set_list(
                'odbc', ['default', 'pyodbc', 'ceODBC'],
                label='ODBC method', order=0,
                description='ODBC method to use.', value=[0],
                editor=synode.Util.combo_editor())

    def _row_changed(self, index):
        self._parameters["table_names"].value = [index]

    def _table_query_button_clicked(self):
        self._parameters["table_query"].value = True
        self._parameters["lineedit_query"].value = False
        self._parameters["custom_query"].value = False
        self._table_query_enable(True)
        self._lineedit_query_enable(False)
        self._custom_query_enable(False)

    def _lineedit_query_button_clicked(self):
        self._parameters["table_query"].value = False
        self._parameters["lineedit_query"].value = True
        self._parameters["custom_query"].value = False
        self._table_query_enable(False)
        self._lineedit_query_enable(True)
        self._custom_query_enable(False)

    def _custom_query_button_clicked(self):
        self._parameters["table_query"].value = False
        self._parameters["lineedit_query"].value = False
        self._parameters["custom_query"].value = True
        self._table_query_enable(False)
        self._lineedit_query_enable(False)
        self._custom_query_enable(True)

    def _table_query_enable(self, state):
        self._table_name_combo.setEnabled(state)
        self._table_name_label.setEnabled(state)

    def _lineedit_query_enable(self, state):
        self._query_edit.setEnabled(state)
        self._query_label.setEnabled(state)

    def _custom_query_enable(self, state):
        self._join_tables.setEnabled(state)
        self._label_join_tables.setEnabled(state)
        self._table_columns.setEnabled(state)
        self._label_table_columns.setEnabled(state)
        self._join_column_selection.setEnabled(state)
        self._label_join_column_selection.setEnabled(state)
        self._join_columns.setEnabled(state)
        self._label_join_columns.setEnabled(state)
        self._label_where_condition.setEnabled(state)
        self._where_column_combo.setEnabled(state)
        self._where_comparison.setEnabled(state)
        self._where_condition.setEnabled(state)
        self._where_add_button.setEnabled(state)
        self._where_condition_list.setEnabled(state)
        self._preview_query.setEnabled(state)
        self._preview_query_button.setEnabled(state)
        self._preview_table.setEnabled(state)
        self._preview_table_button.setEnabled(state)

    def _query_changed(self, text):
        self._parameters["query_str"].value = str(text)

    def _names_changed(self):
        current_join_columns = self._parameters["join_columns"].list
        names = self._join_tables.selectedItems()
        self._parameters["join_tables"].list = [str(name.text())
                                                for name in names]
        columns = []
        columns_with_table = []
        names_text = []

        for name in names:
            name = name.text()
            names_text.append(name)
            [columns.append(column)
             for column in self._db_interface.table_column_names(name)
             if column not in columns]
            [columns_with_table.append(str(name + '.' + column))
             for column in self._db_interface.table_column_names(name)]
            columns.sort()
        columns_with_table.sort()
        current_selected_cols = self._parameters["table_columns"].list
        self._table_columns.clear()
        self._table_columns.addItems(columns_with_table)
        # Mark columns previously selected as selected if column name still in
        # column list.
        for item in current_selected_cols:
            if item in columns_with_table:
                self._table_columns.findItems(
                    item, QtCore.Qt.MatchCaseSensitive)[0].setSelected(True)

        self._join_column_selection.clear()
        self._join_column_selection.addItems(columns_with_table)
        self._parameters["join_column_selection"].list = columns_with_table

        self._join_columns.clear()
        reset_join_on = []
        [reset_join_on.append(str(item))
         for item in current_join_columns
            if item in columns_with_table]
        if len(reset_join_on) != 0:
            self._join_columns.addItems(reset_join_on)
        self._parameters["join_columns"].list = reset_join_on

        # Fix where_columns_combo values
        self._where_column_combo.clear()
        self._where_column_combo.addItems(columns_with_table)
        self._parameters["where_column_combo"].list = columns_with_table
        if self._parameters["where_column_combo"].list:
            self._parameters["where_column_combo"].value = [0]

        # Remove where statements including table names not longer selected
        # for query
        where_statements = self._parameters["where_condition_list"].list
        valid_where_statements = []
        regex = re.compile("^([a-zA-Z0-9_]*).")
        [valid_where_statements.append(where_statement)
            for where_statement in where_statements
            if regex.findall(where_statement)[0] in names_text]

        self._parameters["where_condition_list"].list = valid_where_statements
        self._where_condition_list.clear()
        self._where_condition_list.addItems(valid_where_statements)

    def _columns_changed(self):
        columns = self._table_columns.selectedItems()
        self._parameters["table_columns"].list = (
            [str(column.text()) for column in columns])

    def _add_double_click(self):
        """Add items to join_column list widget."""
        item = self._join_column_selection.currentItem().text()
        self._join_columns.addItem(item)
        items = [str(self._join_columns.item(index).text())
                 for index in range(self._join_columns.count())]
        self._parameters["join_columns"].list = items

    def _remove_double_click(self):
        """Remove items from join_column list widget."""
        item = self._join_columns.currentItem().text()
        items = [str(self._join_columns.item(index).text())
                 for index in range(self._join_columns.count())]
        items.remove(item)
        self._join_columns.clear()
        self._join_columns.addItems(items)
        self._parameters["join_columns"].list = items

    def _change_order(self):
        """Change order on join_columns."""
        self._parameters["join_columns"].list = (
            [str(self._join_columns.item(index).text())
             for index in range(self._join_columns.count())])

    def _change_order_where(self):
        """Change order on where_statements."""
        self._parameters["where_condition_list"].list = (
            [str(self._where_condition_list.item(index).text())
             for index in range(self._where_condition_list.count())])

    def _where_column_changed(self, index):
        if index != -1:
            self._parameters["where_column_combo"].value = []
        else:
            self._parameters["where_column_combo"].value = [index]

    def _where_comparison_changed(self, index):
        self._parameters["where_comparison_combo"].value = [index]

    def _where_condition_changed(self, text):
        self._parameters["where_condition"].value = str(text)

    def _add_where_clause(self):
        where_clause = ''
        condition = self._parameters["where_condition"].value
        if (condition != '' and
                self._parameters["where_column_combo"].selected and
                self._parameters["where_comparison_combo"].selected):
            where_clause += self._parameters["where_column_combo"].selected
            where_clause += self._parameters["where_comparison_combo"].selected
            where_clause += condition
            self._where_condition_list.addItem(where_clause)
            items = [str(
                self._where_condition_list.item(index).text()) for index in
                     range(self._where_condition_list.count())]
            self._parameters["where_condition_list"].list = items

    def _remove_where_condition(self):
        item = self._where_condition_list.currentItem().text()
        items = [str(
            self._where_condition_list.item(index).text()) for index in
                 range(self._where_condition_list.count())]
        items.remove(item)
        self._where_condition_list.clear()
        self._where_condition_list.addItems(items)
        self._parameters["where_condition_list"].list = items

    def _add_preview_table(self):
        """Preview table when button clicked."""
        try:
            query = _build_where_query(
                self._parameters["join_tables"].list,
                self._parameters["table_columns"].list,
                self._parameters["join_columns"].list,
                self._parameters["where_condition_list"].list)

            with self._db_interface.to_rows_query(query) as (
                    tablenames, tabledata):
                tablenames = list(tablenames)
                tabledata = list(tabledata)
                self._preview_table.clear()
                nbr_rows = len(tabledata)
                nbr_cols = len(tablenames)
                self._preview_table.setRowCount(nbr_rows)
                self._preview_table.setColumnCount(nbr_cols)
                self._preview_table.setHorizontalHeaderLabels(tablenames)

                for row_ind, row in enumerate(tabledata):
                    for col_ind, item in enumerate(list(row)):
                        self._preview_table.setItem(
                            row_ind, col_ind,
                            QtWidgets.QTableWidgetItem(str(item)))
        except Exception:
            nbr_rows = 1
            self._preview_table.clear()
            self._preview_table.setRowCount(1)
            self._preview_table.setColumnCount(1)
            self._preview_table.setItem(
                0, 0, QtWidgets.QTableWidgetItem('Not a valid query'))
            self._preview_table.setHorizontalHeaderLabels(['Error'])

        self._preview_table.setVerticalHeaderLabels(
            [str(i) for i in range(nbr_rows)])

    def _add_preview_query(self):
        """Preview query."""
        query = _build_where_query(
            self._parameters["join_tables"].list,
            self._parameters["table_columns"].list,
            self._parameters["join_columns"].list,
            self._parameters["where_condition_list"].list)

        self._preview_query.setText(str(query))
        self._parameters["preview_query"].value = str(query)


class DataImportSQL(importers.TableDataImporterBase):
    """
    Importer for SQL databases.

    If the URL resource contains credential variables for login or token
    credentials these will be entered as part of the URL.

    See :ref:`Credentials Preferences<preferences_credentials>` for more info.
    """
    IMPORTER_NAME = "SQL"
    PARAMETER_VIEW = DataImportSQLWidget
    DATASOURCES = [importers.DATASOURCE.FILE,
                   importers.DATASOURCE.DATABASE]

    def __init__(self, fq_infilename, parameters, **kwargs):
        self._stored_db_interface = None
        super().__init__(fq_infilename, parameters)

    @classmethod
    def supports_datasource(cls) -> bool:
        return True

    def _db_interface(self, resource, capture_exc=True):
        mode = self.input_data().decode_type()

        if resource is None:
            resource = self.input_data().decode_path()
            interface = sql.get_interface_null(resource)
        else:
            interface = sql.get_interface_null(resource)

        if not self._stored_db_interface:
            try:
                if mode == _file_mode:
                    interface = sql.get_interface_file(
                        resource, capture_exc=capture_exc)
                elif mode == _odbc_mode:
                    try:
                        odbc_name = self._parameters['odbc'].selected
                    except KeyError:
                        odbc_name = 'odbc'
                    interface = sql.get_interface_odbc(
                        resource, odbc_name=odbc_name, capture_exc=capture_exc)
                elif mode == _sqlalchemy_mode:
                    interface = sql.get_interface_sqlalchemy(
                        resource, capture_exc=capture_exc)
            except Exception:
                if capture_exc:
                    interface = sql.get_interface_null(resource, sys.exc_info)
                else:
                    raise
            self._stored_db_interface = interface
        return self._stored_db_interface

    def name(self):
        return self.IMPORTER_NAME

    def valid_for_file(self):
        """Return True if input file is a valid SQL file."""
        res = False
        try:
            if self.input_data().decode_type() == _file_mode:
                path = self.input_data().decode_path()
                if path and os.path.isfile(path):
                    interface = sql.get_interface_file(
                        path, read_only=True, connect=False)
                    res = not interface.is_null() and interface.is_valid()
        except Exception:
            pass
        return res

    def parameter_view(self, parameters):
        return DataImportSQLWidget(
            parameters, self.node(), self.input_data(), self._db_interface)

    def _get_credentials_expanded_resource(self):
        res = self.input_data().decode_path()
        if self.input_data().decode_type() in _db_modes:
            res = credentials.get_credentials_expanded_resource(
                self.node(), self.input_data().connection(), _expand_login(
                    self.input_data().decode_type()))
        return res

    def import_data(self, out_datafile, parameters=None, progress=None):
        """Import SQLite data from a file"""
        self._parameters = parameters
        # For auto to work. Need to know table name if not table name selected
        # yet.
        resource = self._get_credentials_expanded_resource()
        try:
            db_interface = self._db_interface(resource, capture_exc=False)
        except Exception as e:
            raise self.import_failed(e)
        if db_interface.is_null():
            print('Unsupported database', file=sys.stderr)

        try:
            lineedit_query = self._parameters['lineedit_query'].value
        except KeyError:
            lineedit_query = False
        try:
            query_str = self._parameters['query_str'].value
        except KeyError:
            query_str = ''
        try:
            custom_query = self._parameters['custom_query'].value
        except KeyError:
            custom_query = False
        try:
            table_name = self._parameters['table_names'].selected
        except KeyError:
            table_name = None

        try:
            join_tables = self._parameters['join_tables'].list
        except Exception:
            join_tables = []

        tabledata = table.File()

        if lineedit_query:
            try:
                with db_interface.to_rows_query(query_str) as (names, rows):
                    tabledata = table.File.from_rows(names, rows)
            except QueryError as e:
                raise exceptions.SyDataError(str(e))
        elif custom_query:
            table_columns = self._parameters['table_columns'].list
            join_columns = self._parameters['join_columns'].list
            where_conditions = (
                self._parameters['where_condition_list'].list)
            query = _build_where_query(
                join_tables, table_columns, join_columns, where_conditions)
            with db_interface.to_rows_query(query) as (names, rows):
                tabledata = table.File.from_rows(names, rows)
        else:
            # TODO(Erik): Make this less questionable. That is, if no table is
            # selected or the selected table does not exist, the first table
            # in the list is selected automatically.
            # Update: Added some feedback for the questionable behaviors.
            table_names = db_interface.table_names()
            if table_names:
                if not table_name:
                    table_name = table_names[0]
                    print(
                        f'Selected table is not set, importing the first '
                        f'table: {table_name} instead.',
                        file=sys.stderr)
                elif table_name not in table_names:
                    table_name = table_names[0]
                    print(
                        f'Selected table is missing, importing the first '
                        f'table: {table_name} instead.',
                        file=sys.stderr)
            else:
                print(
                    'No tables detected in database', file=sys.stderr)
            try:
                with db_interface.to_rows_table(table_name) as (names, rows):
                    tabledata = table.File.from_rows(names, rows)
            except QueryError as e:
                raise exceptions.SyDataError(str(e))

        out_datafile.update(tabledata)
