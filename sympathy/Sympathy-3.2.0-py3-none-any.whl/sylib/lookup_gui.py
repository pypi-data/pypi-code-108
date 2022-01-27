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
from sympathy.api import qt2 as qt

from . widget_library import FilterListView

QtCore = qt.QtCore
QtGui = qt.import_module("QtGui")
QtWidgets = qt.import_module("QtWidgets")


class ValuePreviewCell(QtWidgets.QTableWidgetItem):
    """A specialized QTableWidgetItem that displays the contents in greyed out
    italic text.
    """

    def __init__(self, *args, **kwargs):
        super(ValuePreviewCell, self).__init__(*args, **kwargs)
        font = self.font()
        font.setPointSize(0.9 * font.pointSize())
        font.setItalic(True)
        self.setFont(font)


class LookupWidget(QtWidgets.QWidget):
    """Main configuration widget for the Lookup node."""

    def __init__(
            self, parameter_root, template_file, lookupee_file,
            *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._parameter_root = parameter_root
        self._template_file = template_file
        self._lookupee_file = lookupee_file

        self._init_gui()

        if self._template_file.is_valid():
            template_signals = self._template_file.column_names()
            self.template_signals_list.add_items(template_signals)

        if self._lookupee_file.is_valid():
            lookupee_signals = self._lookupee_file.column_names()
            self.lookupee_signals_list.add_items(lookupee_signals)

        self.update_lookup_table()

    def _init_gui(self):
        signal_lists_layout = QtWidgets.QHBoxLayout()
        self.template_signals_list = FilterListView(header="Lookup columns")
        self.template_signals_list.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        signal_lists_layout.addWidget(self.template_signals_list)
        self.lookupee_signals_list = FilterListView(header="Control columns")
        self.lookupee_signals_list.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        signal_lists_layout.addWidget(self.lookupee_signals_list)

        add_button = QtWidgets.QPushButton("Add pair")
        remove_button = QtWidgets.QPushButton("Remove pair")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()

        lookup_table_label = QtWidgets.QLabel("Matching column pairs")
        table_headers = ["Lookup column", "Value preview",
                         "Control column", "Value preview", "Event column"]
        self.lookup_table_widget = QtWidgets.QTableWidget(0, len(table_headers))
        self.lookup_table_widget.verticalHeader().hide()
        self.lookup_table_widget.setHorizontalHeaderLabels(table_headers)
        self.lookup_table_widget.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.lookup_table_widget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.lookup_table_widget.setAlternatingRowColors(True)
        self.lookup_table_widget.resizeColumnsToContents()
        lookup_table_layout = QtWidgets.QVBoxLayout()
        lookup_table_layout.addWidget(lookup_table_label)
        lookup_table_layout.addWidget(self.lookup_table_widget)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addItem(signal_lists_layout)
        vlayout.addItem(button_layout)
        vlayout.addItem(lookup_table_layout)
        vlayout.addWidget(self._parameter_root['perfect_match'].gui())
        vlayout.addWidget(self._parameter_root['nomasks'].gui())
        vlayout.addWidget(self._parameter_root['copy_input'].gui())
        self.setLayout(vlayout)

        delete_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Delete),
            self.lookup_table_widget)

        # Connect signals
        delete_shortcut.activated.connect(self.remove_button_clicked)
        add_button.clicked.connect(self.add_button_clicked)
        remove_button.clicked.connect(self.remove_button_clicked)
        self.lookup_table_widget.itemChanged.connect(
            self.lookup_table_item_changed)

    def update_lookup_table(self):
        """Fill the lookup table with values from the parameter root and if
        possible with previews of the values from the table file.
        """
        self.lookup_table_widget.setRowCount(
            len(self._parameter_root['template_columns'].list))
        event_col = self._parameter_root['event_column'].value

        for i, (template_col, lookupee_col) in enumerate(zip(
                self._parameter_root['template_columns'].list,
                self._parameter_root['lookupee_columns'].list)):

            template_value = ""
            if (self._template_file.is_valid() and
                    template_col in self._template_file):
                template_values = self._template_file.get_column_to_array(
                    template_col)
                if template_values.size != 0:
                    template_value = template_values[0]
            self.lookup_table_widget.setItem(
                i, 0, QtWidgets.QTableWidgetItem(template_col))
            self.lookup_table_widget.setItem(
                i, 1, ValuePreviewCell(str(template_value)))

            lookupee_value = ""
            if (self._lookupee_file.is_valid() and
                    lookupee_col in self._lookupee_file):
                lookupee_values = self._lookupee_file.get_column_to_array(
                    lookupee_col)
                if lookupee_values.size != 0:
                    lookupee_value = lookupee_values[0]
            self.lookup_table_widget.setItem(
                i, 2, QtWidgets.QTableWidgetItem(lookupee_col))
            self.lookup_table_widget.setItem(
                i, 3, ValuePreviewCell(str(lookupee_value)))

            event_col_item = QtWidgets.QTableWidgetItem("")
            event_col_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            if event_col == i:
                event_col_item.setCheckState(QtCore.Qt.Checked)
            else:
                event_col_item.setCheckState(QtCore.Qt.Unchecked)

            self.lookup_table_widget.blockSignals(True)
            self.lookup_table_widget.setItem(i, 4, event_col_item)
            self.lookup_table_widget.blockSignals(False)

    def add_button_clicked(self, state=None):
        """Add a new lookup consisting of the selected lines in the two signal
        lists.
        """
        if (self.template_signals_list.list_widget.currentItem() and
                self.lookupee_signals_list.list_widget.currentItem()):
            for pname, widget in [
                    ('template_columns', self.template_signals_list),
                    ('lookupee_columns', self.lookupee_signals_list)]:
                new_item = widget.list_widget.currentItem().text()
                parameter = self._parameter_root[pname]
                parameter.list = parameter.list + [new_item]
            self.update_lookup_table()

    def remove_button_clicked(self, state=None):
        event_col = self._parameter_root['event_column'].value

        selected_rows = [
            selected.row()
            for selected in self.lookup_table_widget.selectedIndexes()]
        selected_rows = sorted(set(selected_rows))

        for row in reversed(selected_rows):
            for pname in ['template_columns', 'lookupee_columns']:
                parameter = self._parameter_root[pname]
                list_ = parameter.list
                del list_[row]
                parameter.list = list_

            if row == event_col:
                event_col = -1
            elif row < event_col:
                event_col -= 1

        if event_col >= 0:
            self.lookup_table_widget.blockSignals(True)
            self.lookup_table_widget.item(event_col, 4).setCheckState(
                QtCore.Qt.Checked)
            self.lookup_table_widget.blockSignals(False)

        self._parameter_root['event_column'].value = event_col
        self.update_lookup_table()

    def lookup_table_item_changed(self, changed_item):
        """Called whenever an item in the lookup table changed. Make sure that
        only one column is selected as event column.
        """
        if changed_item.column() == 4:
            if changed_item.checkState() == QtCore.Qt.Checked:
                self._parameter_root['event_column'].value = changed_item.row()
                for row in range(self.lookup_table_widget.rowCount()):
                    item = self.lookup_table_widget.item(row, 4)
                    if item and row != changed_item.row():
                        self.lookup_table_widget.blockSignals(True)
                        item.setCheckState(QtCore.Qt.Unchecked)
                        self.lookup_table_widget.blockSignals(False)
            else:
                self._parameter_root['event_column'].value = -1
