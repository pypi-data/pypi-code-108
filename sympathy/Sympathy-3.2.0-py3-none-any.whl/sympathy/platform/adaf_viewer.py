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
import re
import numpy as np

from Qt import QtCore, QtWidgets, QtGui

from sympathy.utils import prim
from . import widget_library as sywidgets
from .viewerbase import ViewerBase
from .table_viewer import dtype_color, TableViewer

def combined(string):
    def to_int(string):
        try:
            return int(string)
        except ValueError:
            return string
    return [to_int(part) for part in re.split('([0-9]+)', string)]


class FixedTableModel(QtCore.QAbstractTableModel):

    system_role, raster_role, signal_role = range(
        QtCore.Qt.UserRole, QtCore.Qt.UserRole + 3)

    def __init__(self, parent=None):
        self._rows = []
        self._data = None
        self._headers = ['System', 'Raster', 'Signal', 'Rows x Columns']
        super().__init__(parent)

    def set_data(self, data):
        if data is self._data:
            return

        self.beginResetModel()
        self._rows = []
        self._data = data
        for system_name, system in data.info()['sys'].items():
            for raster_name, raster in system.items():
                rows, cols = raster['shape']
                for signal_name in raster['signals']:
                    self._rows.append(
                        (system_name, raster_name, signal_name,
                         f'{rows} x '
                         f'{cols}',
                         raster))
        self.endResetModel()

    def rowCount(self, index=None):
        return len(self._rows)

    def columnCount(self, index=None):
        return len(self._headers)

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == QtCore.Qt.DisplayRole:
            return self._rows[row][col]
        elif role == self.system_role:
            return self._rows[row][0]
        elif role == self.raster_role:
            return self._rows[row][1]
        elif role == self.signal_role:
            return self._rows[row][2]
        elif role == QtCore.Qt.BackgroundRole:
            raster = self._rows[row][4]
            column_name = self._rows[row][2]
            column_type = np.dtype(raster['signals'][column_name]['dtype'])
            return dtype_color(column_type)
        return None

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._headers[section]
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return str(section)
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
        return super().headerData(section, orientation, role)

    def reset(self):
        self.beginResetModel()
        self._rows = []
        self._data = None
        self.endResetModel()

    def clear(self):
        self.reset()


class SearchWidget(QtWidgets.QWidget):

    # (system_name, raster_name, signal_name)
    selected_item = QtCore.Signal(tuple)
    finished = QtCore.Signal()

    _path_role, _signal_role = range(
        QtCore.Qt.UserRole, QtCore.Qt.UserRole + 2)

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()

        self._data = data

        search_layout = QtWidgets.QFormLayout()
        search_layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.FieldsStayAtSizeHint)

        search_layout.setFormAlignment(QtCore.Qt.AlignLeft)
        search_layout.setLabelAlignment(QtCore.Qt.AlignVCenter)

        self._result_table = sywidgets.BasePreviewTable()
        self._result_table.setToolTip(
            'Double-click or use menu to go to Signal Location.')

        self._result_table.add_context_menu_action(
            'Go to Signal Location',
            self._jump_to_signal_location,
            prim.get_icon_path('actions/view-jump-to-row-symbolic.svg'),
            validate_callback=self._validate_jump)

        self._result_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self._result_table.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self._result_model = FixedTableModel()

        self._search_model = sywidgets.OrderedSearchFilterModel(
            self._result_table)
        self._search_model.setSourceModel(self._result_model)
        self._result_table.setModel(self._search_model)
        self._search_model.setFilterRole(FixedTableModel.signal_role)

        layout.addLayout(search_layout)
        layout.addWidget(self._result_table)

        self.setLayout(layout)

        self._result_table.doubleClicked.connect(
            self._handle_result_table_double_clicked)

    def _validate_jump(self, row, column):
        return row >= 0 and column >= 0

    def _jump_to_signal_location(self, row, column):
        index = self._search_model.index(row, column)
        if index.isValid():
            self._index_accepted(index)

    def set_filter(self, text):
        self._search_model.set_filter(text)

    def _update(self):
        # Avoid update when not searching.
        self._result_model.set_data(self._data)

    def setVisible(self, visible):
        super().setVisible(visible)

        if visible:
            # Avoid update when not searching.
            self._update()

    def update_data(self, data):
        self._data = data
        if data is not self._data:
            self._result_model.clear()

        if self.isVisible():
            # Avoid update when not searching.
            self._update()

    def _handle_result_table_double_clicked(self, index):
        self._index_accepted(index)

    def _index_accepted(self, index):
        self.selected_item.emit((
            index.data(FixedTableModel.system_role),
            index.data(FixedTableModel.raster_role),
            index.data(FixedTableModel.signal_role)))
        self.finished.emit()


class ADAFViewer(ViewerBase):
    def __init__(self, adaf_data=None, console=None, parent=None):
        super().__init__(parent)

        self._adaf = adaf_data
        self._meta_table = None
        self._result_table = None

        self._init_gui()

        self.update_data(adaf_data)

    def adaf(self):
        return self._adaf

    def data(self):
        return self.adaf()

    def _update_rasters(self, rasters, name):
        self._raster_combo.clear()
        self._raster_combo.addItems(rasters)

        if name in rasters:
            self._raster_combo.setCurrentIndex(
                self._raster_combo.findText(
                    name,
                    QtCore.Qt.MatchExactly))
        elif len(rasters):
            self._raster_combo.setCurrentIndex(0)

    def update_data(self, adaf_data):

        if adaf_data is not None:
            self._adaf = adaf_data
            self._meta_table = self._adaf.meta.to_table()
            self._meta_table.set_name('Meta')
            self._meta_viewer.update_data(self._meta_table)

            self._result_table = self._adaf.res.to_table()
            self._result_table.set_name('Result')
            self._result_viewer.update_data(self._result_table)

            self._search_widget.update_data(self._adaf)

            prev_system_name = str(
                self._system_combo.currentText())
            prev_raster_name = str(
                self._raster_combo.currentText())

            systems = [self._system_combo.itemText(i)
                       for i in range(self._system_combo.count())]

            rasters = [self._raster_combo.itemText(i)
                       for i in range(self._raster_combo.count())]

            new_systems = sorted(adaf_data.sys.keys(), key=combined)
            try:
                prev_system = adaf_data.sys[prev_system_name]
            except KeyError:
                system_names = adaf_data.sys.keys()
                if len(system_names):
                    prev_system = adaf_data.sys[system_names[0]]
                else:
                    self._system_combo.clear()
                    self._raster_combo.clear()
                    self._raster_viewer.clear()
                    return

            new_rasters = sorted(prev_system.keys(), key=combined)

            if systems != new_systems:
                self._raster_viewer.clear()
                self._system_combo.clear()
                self._system_combo.addItems(new_systems)

                if prev_system_name in new_systems:
                    self._system_combo.setCurrentIndex(
                        self._system_combo.findText(
                            prev_system_name,
                            QtCore.Qt.MatchExactly))

                    if rasters != new_rasters:
                        self._update_rasters(new_rasters, prev_raster_name)

            elif rasters != new_rasters:
                self._raster_viewer.clear()
                self._update_rasters(new_rasters, prev_raster_name)

            self._change_raster_using_system(
                self._raster_combo.currentText(),
                self._system_combo.currentText())

    def _init_gui(self):
        layout = QtWidgets.QVBoxLayout()

        tabwidget = QtWidgets.QTabWidget()

        self._meta_viewer = TableViewer(
            self._meta_table, show_title=False, plot=False)
        tabwidget.addTab(self._meta_viewer, 'Meta')

        self._result_viewer = TableViewer(
            self._result_table, show_title=False, plot=False)
        tabwidget.addTab(self._result_viewer, 'Result')

        self._system_combo = QtWidgets.QComboBox()
        self._raster_combo = QtWidgets.QComboBox()

        system_layout = QtWidgets.QHBoxLayout()
        system_layout.setContentsMargins(11, 2, 11, 0)

        self._system_label = QtWidgets.QLabel('System')
        self._raster_label = QtWidgets.QLabel('Raster')

        system_layout.addWidget(self._system_label)
        system_layout.addWidget(self._system_combo)
        system_layout.addWidget(self._raster_label)
        system_layout.addWidget(self._raster_combo)

        self._search_label = QtWidgets.QLabel('Signal')
        self._search_line =  sywidgets.ClearButtonLineEdit(
            placeholder='Filter', clear_button=True)
        self._search_line.setToolTip(
            'Search for signal name in all rasters and systems')

        system_layout.addWidget(self._search_label)
        system_layout.addWidget(self._search_line)

        self._search_widget = SearchWidget(self._adaf)

        self._search_button = sywidgets.FilterButton()
        self._search_button.setToolTip('Search for Rasters.')

        # wrap it in a widget, so it gets aligned with the table viewer
        system_widget = QtWidgets.QWidget()
        policy = system_widget.sizePolicy()
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Minimum)
        policy.setHorizontalStretch(0)
        system_widget.setSizePolicy(policy)
        system_widget.setLayout(system_layout)

        system_layout.addStretch(1)
        system_layout.addWidget(self._search_button, alignment=QtCore.Qt.AlignRight)

        self._raster_viewer = TableViewer(plot=True, show_title=False)

        timeseries_layout = QtWidgets.QVBoxLayout()
        timeseries_layout.setContentsMargins(5, 5, 5, 5)
        timeseries_layout.setSpacing(0)
        timeseries_layout.addWidget(system_widget)
        timeseries_layout.addWidget(self._raster_viewer, stretch=1)
        timeseries_layout.addWidget(self._search_widget)

        timeseries_widget = QtWidgets.QWidget()
        timeseries_widget.setLayout(timeseries_layout)
        tabwidget.addTab(timeseries_widget, 'Timeseries')

        layout.addWidget(tabwidget)

        self.setLayout(layout)

        self._system_combo.currentIndexChanged[int].connect(
            self._system_changed)
        self._raster_combo.currentIndexChanged[int].connect(
            self._raster_changed)
        self._search_button.toggled.connect(self._search_toggled)
        self._search_widget.selected_item.connect(
            self._search_selection_changed)
        self._search_widget.finished.connect(self._search_finished)
        self._search_line.textChanged.connect(self._search_widget.set_filter)
        self._search_toggled(False)

    def _system_changed(self, system_idx):
        system_name = self._system_combo.currentText()
        if system_name not in self._adaf.sys.keys():
            return
        rasters = self._adaf.sys[system_name].keys()

        try:
            prev_raster_name = str(
                self._raster_combo.currentText())
        except AttributeError:
            prev_raster_name = None

        self._update_rasters(rasters, prev_raster_name)

    def _change_raster_using_system(self, raster_name, system_name):
        if not raster_name or not system_name:
            self._raster_viewer.clear()
        else:
            raster = self._adaf.sys[system_name][raster_name]
            raster_table = raster.to_table('({})'.format(raster_name))
            raster_table.set_name(raster_name)
            self._raster_viewer.update_data(raster_table)

    def _raster_changed(self, raster_idx):
        raster_name = self._raster_combo.currentText()
        system_name = self._system_combo.currentText()
        current_system_idx = self._system_combo.currentIndex()
        if current_system_idx is None:
            return
        self._change_raster_using_system(
            str(raster_name), system_name)

    def _search_toggled(self, enabled):
        for widget in [
                self._search_label,
                self._search_line,
                self._search_widget]:
            widget.setVisible(enabled)

        for widget in [
                self._raster_viewer,
                self._system_label,
                self._system_combo,
                self._raster_label,
                self._raster_combo]:
            widget.setVisible(not enabled)

    def _search_selection_changed(self, selection):
        system, raster, signal = selection

        self._system_combo.setCurrentIndex(
            self._system_combo.findText(
                system, QtCore.Qt.MatchCaseSensitive))

        self._raster_combo.setCurrentIndex(
            self._raster_combo.findText(
                raster, QtCore.Qt.MatchCaseSensitive))

    def _search_finished(self):
        self._search_button.setChecked(False)

    def custom_menu_items(self):
        return []
