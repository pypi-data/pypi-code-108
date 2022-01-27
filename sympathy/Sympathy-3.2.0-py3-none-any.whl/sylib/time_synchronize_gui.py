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
import collections
import numpy as np
from datetime import datetime as dt
from sympathy.api import qt2 as qt_compat
import warnings
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.dates import DateFormatter, date2num

warnings.warn(
    "sylib.time_synchronize_gui module is deprecated "
    "and will be removed in version 4.0.0.",
    FutureWarning)
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    from . synchronize import SynchronizeTime

QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')
qt_compat.backend.use_matplotlib_qt()


def system_signal_map(datafile):
    system_signal_dict = collections.defaultdict(list)
    if datafile.is_valid():
        for signal_name, signal in datafile.ts.items():
            system_name = signal.system_name()
            system_signal_dict[system_name].append(signal_name)
        for system_name in system_signal_dict:
            system_signal_dict[system_name].sort()
    return system_signal_dict


class TimeSynchronizeWidget(QtWidgets.QWidget):
    def __init__(self, params, datafile, parent=None):
        super(TimeSynchronizeWidget, self).__init__(parent)
        self._data = params
        self._datafile = datafile
        self.sync = SynchronizeTime()

        if self._datafile.is_valid():
            self.system_signal_dict = system_signal_map(self._datafile)
        else:
            self.system_signal_dict = {}

        # Default sync signals for different systems
        self._default_system_sync_signals = {}
        self._default_system_sync_signals['Vetsone'] = ['SPEED']
        self._default_system_sync_signals['HEAD'] = ['SPEED']
        self._default_system_sync_signals['DIVA'] = ['SPEED']
        self._default_system_sync_signals['INCA'] = [
            'VehV_v', 'Scm_VSpd_Fine\\ETKC:1',
            'Scm_VSpd\\ETKC:1', 'vfzg_w\\ETKC:1']

        self._init_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()

        gridlayout = QtWidgets.QGridLayout()
        gridlayout.setSpacing(10)
        gridlayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        gridlayout.setColumnStretch(2, 1)
        gridlayout.setRowStretch(1, 2)

        # Reference

        # Reference system
        refsystem_label = QtWidgets.QLabel("Reference system")
        self.refsystem_combobox = QtWidgets.QComboBox()
        self.refsystem_combobox.setFixedWidth(150)
        self.refsystem_model = QtGui.QStandardItemModel()
        self.refsystem_combobox.setModel(self.refsystem_model)

        self._init_combobox(self.refsystem_combobox,
                            self.refsystem_model,
                            [''] + list(self.system_signal_dict.keys()),
                            self._data['refsystem'])

        # Reference signal
        refsignal_label = QtWidgets.QLabel("Reference signal")
        self.refsignal_combobox = QtWidgets.QComboBox()
        self.refsignal_model = QtGui.QStandardItemModel()
        self.refsignal_combobox.setModel(self.refsignal_model)

        current_refsystem_name = self.refsystem_combobox.currentText()

        self._init_combobox(self.refsignal_combobox,
                            self.refsignal_model,
                            self.system_signal_dict.get(
                                current_refsystem_name, []),
                            self._data['refsignal'],
                            current_refsystem_name)

        # Syncee

        # Syncee system
        synceesystem_label = QtWidgets.QLabel("Syncee system")
        self.synceesystem_combobox = QtWidgets.QComboBox()
        self.synceesystem_combobox.setFixedWidth(150)
        self.synceesystem_model = QtGui.QStandardItemModel()
        self.synceesystem_combobox.setModel(self.synceesystem_model)

        self._init_combobox(self.synceesystem_combobox,
                            self.synceesystem_model,
                            [''] + list(self.system_signal_dict.keys()),
                            self._data['synceesystem'])

        # Syncee signal
        synceesignal_label = QtWidgets.QLabel("Syncee signal")
        self.synceesignal_combobox = QtWidgets.QComboBox()
        self.synceesignal_model = QtGui.QStandardItemModel()
        self.synceesignal_combobox.setModel(self.synceesignal_model)

        current_synceesystem_name = self.synceesystem_combobox.currentText()

        self._init_combobox(self.synceesignal_combobox,
                            self.synceesignal_model,
                            self.system_signal_dict.get(
                                current_synceesystem_name, []),
                            self._data['synceesignal'],
                            current_synceesystem_name)

        # VJoin signal
        vjoin_index_label = QtWidgets.QLabel("VJoin signal")
        self.vjoin_index_combobox = QtWidgets.QComboBox()
        self.vjoin_index_model = QtGui.QStandardItemModel()
        self.vjoin_index_combobox.setModel(self.vjoin_index_model)

        current_vjoin_index_name = self.vjoin_index_combobox.currentText()

        self._init_combobox(self.vjoin_index_combobox,
                            self.vjoin_index_model,
                            self.system_signal_dict.get(
                                current_synceesystem_name, []),
                            self._data['vjoin_index'],
                            current_vjoin_index_name,
                            can_be_empty=True)

        # Threshold
        threshold_label = QtWidgets.QLabel("Threshold")
        self._threshold_gui = self._data['threshold'].gui()
        self.threshold_lineedit = self._threshold_gui.editor()
        self.threshold_lineedit.setFixedWidth(40)

        # Synchronization strategies
        syncstrategy_label = QtWidgets.QLabel("Sync strategy")
        self.syncstrategy_combobox = QtWidgets.QComboBox()
        self.syncstrategy_combobox.setFixedWidth(180)
        self.syncstrategy_model = QtGui.QStandardItemModel()
        self.syncstrategy_combobox.setModel(self.syncstrategy_model)

        self._init_combobox(self.syncstrategy_combobox,
                            self.syncstrategy_model,
                            self.sync.strategies(),
                            self._data['syncstrategy'],
                            self.sync.strategy_docs())

        self.result_label = QtWidgets.QLabel("")

        self.sync_button = QtWidgets.QPushButton("&View")
        self.sync_button.setFixedWidth(100)

        gridlayout.addWidget(refsystem_label, 1, 0)
        gridlayout.addWidget(self.refsystem_combobox, 1, 1)
        gridlayout.addWidget(refsignal_label, 2, 0)
        gridlayout.addWidget(self.refsignal_combobox, 2, 1)
        gridlayout.addWidget(synceesystem_label, 3, 0)
        gridlayout.addWidget(self.synceesystem_combobox, 3, 1)
        gridlayout.addWidget(synceesignal_label, 4, 0)
        gridlayout.addWidget(self.synceesignal_combobox, 4, 1)
        gridlayout.addWidget(vjoin_index_label, 5, 0)
        gridlayout.addWidget(self.vjoin_index_combobox, 5, 1)
        gridlayout.addWidget(threshold_label, 6, 0)
        gridlayout.addWidget(self.threshold_lineedit, 6, 1)
        gridlayout.addWidget(syncstrategy_label, 7, 0)
        gridlayout.addWidget(self.syncstrategy_combobox, 7, 1)

        plot_vlayout = QtWidgets.QVBoxLayout()

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setVerticalStretch(1)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.canvas.setSizePolicy(policy)

        plot_vlayout.addWidget(self.canvas)

        # Default navigation toolbar for matplotlib.
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        plot_vlayout.addWidget(self.mpl_toolbar)

        vlayout.addItem(gridlayout)
        vlayout.addWidget(self.result_label)
        vlayout.addWidget(self.sync_button)
        vlayout.addItem(QtWidgets.QSpacerItem(1, 250))
        hlayout.addItem(vlayout)
        hlayout.addItem(plot_vlayout)
        self.setLayout(hlayout)

        self.refsystem_combobox.currentIndexChanged[int].connect(
            self.refsystem_change)
        self.refsignal_combobox.currentIndexChanged[int].connect(
            self.refsignal_change)
        self.synceesystem_combobox.currentIndexChanged[int].connect(
            self.synceesystem_change)
        self.synceesignal_combobox.currentIndexChanged[int].connect(
            self.synceesignal_change)
        self.vjoin_index_combobox.currentIndexChanged[int].connect(
            self.vjoin_index_change)
        self.syncstrategy_combobox.currentIndexChanged[int].connect(
            self.syncstrategy_change)
        self.sync_button.clicked[bool].connect(self._synchronize)

        self._check_signals()

    def refsystem_change(self):
        self._system_change(self.refsystem_combobox,
                            self.refsignal_combobox,
                            self.refsignal_model)
        self._data['refsystem'].value = (
            self.refsystem_combobox.currentText())
        self._data['refsignal'].value = (
            self.refsignal_combobox.currentText())
        self._check_signals()

    def refsignal_change(self):
        self._data['refsignal'].value = (
            self.refsignal_combobox.currentText())
        self._check_signals()

    def synceesystem_change(self):
        self._system_change(self.synceesystem_combobox,
                            self.synceesignal_combobox,
                            self.synceesignal_model)
        self._data['synceesystem'].value = (
            self.synceesystem_combobox.currentText())
        self._data['synceesignal'].value = (
            self.synceesignal_combobox.currentText())
        self._check_signals()

    def synceesignal_change(self):
        self._data['synceesignal'].value = (
            self.synceesignal_combobox.currentText())
        self._check_signals()

    def vjoin_index_change(self):
        self._data['vjoin_index'].value = (
            self.vjoin_index_combobox.currentText())

    def syncstrategy_change(self):
        self._data['syncstrategy'].value = (
            self.syncstrategy_combobox.currentText())

    def _synchronize(self):
        refsignal = self.refsignal_combobox.currentText()
        synceesignal = self.synceesignal_combobox.currentText()
        threshold = self._data['threshold'].value
        syncstrategy = self.syncstrategy_combobox.currentText()
        vjoin_name = self.vjoin_index_combobox.currentText() or None

        sync = SynchronizeTime()
        ref, syncee = sync.time_and_speed_from_file(
            self._datafile, refsignal, synceesignal)
        raster = self._datafile.sys[syncee.system_name()][syncee.raster_name()]

        if vjoin_name in raster:
            index = raster[vjoin_name].y
        else:
            index = np.array([0] * syncee.t.size)

        if self._datafile.is_valid():
            offsets = sync.synchronize_file(
                self._datafile, refsignal, synceesignal, threshold,
                syncstrategy, vjoin_name)
        else:
            offsets = [None] * len(np.unique(index))

        synced_time = sync.apply_offsets(syncee.t, offsets, index)
        self._plot(ref, syncee, synced_time)

    def _plot(self, ref, syncee, synced_time):
        is_datetime = False
        self.axes.clear()
        try:
            if (len(synced_time) and len(ref.t) and len(syncee.t) and
                    isinstance(synced_time[0], np.datetime64) and
                    isinstance(ref.t[0], np.datetime64) and
                    isinstance(syncee.t[0], np.datetime64)):
                is_datetime = True
        except TypeError:
            is_datetime = False
        if ref:
            rt = date2num(ref.t.astype(dt)) if is_datetime else ref.t
            self.axes.plot(
                rt, ref.y, '.-', color='yellow', linewidth=10,
                label='Reference')
        if syncee:
            st = date2num(syncee.t.astype(dt)) if is_datetime else syncee.t
            self.axes.plot(
                st, syncee.y, '.-', color='blue', linewidth=3,
                label='Unsynched')
            if synced_time is not None:
                syt = (date2num(synced_time.astype(dt))
                       if is_datetime else synced_time)
                self.axes.plot(
                    syt, syncee.y, '.-', color='black', linewidth=3,
                    label='Syncee')
            else:
                self.axes.set_title('Test not syncronized (Syncee offset: 0)')
            if is_datetime:
                self.axes.xaxis_date()
                self.axes.set_xticklabels(
                    self.axes.xaxis.get_majorticklabels(), rotation=30)
                self.axes.xaxis.set_major_formatter(
                    DateFormatter('%Y-%m-%d %H:%M:%S'))
                self.figure.autofmt_xdate()
                self.figure.tight_layout()
        self.axes.grid()
        self.axes.legend()
        self.canvas.draw()

    def _system_change(self, system_combobox, signal_combobox, signal_model):
        signal_combobox.blockSignals(True)
        signal_model.clear()
        current_system_name = system_combobox.currentText()
        for item in self.system_signal_dict[current_system_name]:
            signal_model.appendRow(QtGui.QStandardItem(item))
        signal_combobox.blockSignals(False)
        self._set_default_signal(current_system_name, signal_combobox)

    def _set_default_signal(self, system_name, combobox):
        """
        Tries to find the one of the default signals for this system and set
        combobox to that signal. If none of the default signal is found the
        combobox will be set to its first item.
        """
        index = 0
        if system_name in self._default_system_sync_signals:
            default_signals = self._default_system_sync_signals[system_name]
            signals = self.system_signal_dict[system_name]
            for default_signal in default_signals:
                if default_signal in signals:
                    index = signals.index(default_signal)
                    break

        combobox.setCurrentIndex(index)

    def _init_combobox(self, combobox, model, items, init_item,
                       tooltips=None, can_be_empty=False):
        for item in items:
            model.appendRow(QtGui.QStandardItem(item))
        if tooltips:
            for i, tooltip in enumerate(tooltips):
                combobox.setItemData(i, tooltip, QtCore.Qt.ToolTipRole)

        if can_be_empty:
            model.insertRow(0, QtGui.QStandardItem(''))

        if not init_item.value and not can_be_empty:
            combobox.setCurrentIndex(0)
            init_item.value = combobox.currentText()
        elif init_item.value in items:
            index = items.index(init_item.value)
            if can_be_empty:
                index += 1
            combobox.setCurrentIndex(index)
        else:
            combobox.setCurrentIndex(0)

    def _init_or_default_combobox(self, combobox, model,
                                  items, init_item, system_name):
        for item in items:
            model.appendRow(QtGui.QStandardItem(item))

        if init_item.value:
            self._set_default_signal(system_name, combobox)
            init_item.value = combobox.currentText()
        elif init_item.value in items:
            combobox.setCurrentIndex(items.index(init_item.value))
        else:
            model.appendRow(QtGui.QStandardItem(init_item.value))
            combobox.setCurrentIndex(model.rowCount() - 1)

    def _check_signals(self):
        """
        Check if both systems and both signals exist in input and en-/disable
        the view button.
        """
        current_synceesystem = self.synceesystem_combobox.currentText()
        current_refsystem = self.refsystem_combobox.currentText()

        if not (self._data['synceesystem'].value in
                self.system_signal_dict and
                self._data['synceesignal'].value in
                self.system_signal_dict[current_synceesystem] and
                self._data['refsystem'].value in
                self.system_signal_dict and
                self._data['refsignal'].value in
                self.system_signal_dict[current_refsystem]):
            self.sync_button.setEnabled(False)
        else:
            self.sync_button.setEnabled(self._datafile.is_valid())
