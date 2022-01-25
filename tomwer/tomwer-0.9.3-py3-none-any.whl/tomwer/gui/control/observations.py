# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "31/05/2018"


from silx.gui import qt
from collections import OrderedDict
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.blissscan import BlissScan
import weakref
import os


class ScanObservation(qt.QWidget):
    """Widget used for the scans observation"""

    HEADER = ("acquisition", "status", "N projections", "type")

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self._onGoingObservations = None
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(qt.QLabel(""))

        self.observationTable = qt.QTableView(parent=parent)
        self.observationTable.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.observationTable.setModel(
            _ObservedScanModel(parent=self.observationTable, header=self.HEADER)
        )
        self.observationTable.resizeColumnsToContents()
        self.observationTable.setSortingEnabled(True)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        self.layout().addWidget(self.observationTable)
        header = self.observationTable.horizontalHeader()
        if qt.qVersion() < "5.0":
            setResizeMode = header.setResizeMode
        else:
            setResizeMode = header.setSectionResizeMode
        setResizeMode(0, qt.QHeaderView.Fixed)
        setResizeMode(1, qt.QHeaderView.Stretch)
        setResizeMode(2, qt.QHeaderView.Stretch)

        header.setSectionResizeMode(0, qt.QHeaderView.Interactive)
        header.setStretchLastSection(True)

    @property
    def onGoingObservations(self):
        if self._onGoingObservations:
            return self._onGoingObservations()
        else:
            return None

    def setOnGoingObservations(self, onGoingObservations):
        """
        will update the table to display the observations contained in
        onGoingObservations

        :param onGoingObservations: the obsevations observed to display
        """
        if self.onGoingObservations:
            self.onGoingObservations.sigObsAdded.disconnect(self.addObservation)
            self.onGoingObservations.sigObsRemoved.disconnect(self.removeObservation)
            self.onGoingObservations.sigObsStatusReceived.disconnect(self.update)

        self._onGoingObservations = weakref.ref(onGoingObservations)
        self.onGoingObservations.sigObsAdded.connect(self.addObservation)
        self.onGoingObservations.sigObsRemoved.connect(self.removeObservation)
        self.onGoingObservations.sigObsStatusReceived.connect(self.update)

    def update(self, scan, status):
        """

        :param str scan: the updated scan
        :param str status: the status of the updated scan
        """
        self.observationTable.model().update(scan, status)

    def addObservation(self, scan):
        """

        :param scan: the scan observed
        """
        self.observationTable.model().add(scan, "starting")

    def removeObservation(self, scan):
        """

        :param scan: the scan removed
        """
        self.observationTable.model().remove(scan)

    def clear(self):
        self.observationTable.model().clear()


class _ObservedScanModel(qt.QAbstractTableModel):
    def __init__(self, parent, header, *args):
        qt.QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self.observations = OrderedDict()

    def add(self, scan, status):
        self.observations[scan] = status
        if qt.qVersion() > "4.6":
            self.endResetModel()

    def remove(self, scan):
        if scan in self.observations:
            del self.observations[scan]
        if qt.qVersion() > "4.6":
            self.endResetModel()

    def update(self, scan, status):
        self.observations[scan] = status
        if qt.qVersion() > "4.6":
            self.endResetModel()

    def clear(self):
        self.observations = OrderedDict()
        if qt.qVersion() > "4.6":
            self.endResetModel()

    def rowCount(self, parent=None):
        return len(self.observations)

    def columnCount(self, parent=None):
        return len(self.header)

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        if self.observations is None:
            return

        to_order = {}
        for observation in self.observations.keys():
            to_order[str(observation)] = observation

        ordering = sorted(list(to_order.keys()))
        if order == qt.Qt.DescendingOrder:
            ordering = reversed(ordering)
        _observations = OrderedDict()
        for str_key in ordering:
            key = to_order[str_key]
            _observations[key] = self.observations[key]

        self.observations = _observations
        self.layoutChanged.emit()

    def data(self, index, role):
        if index.isValid() is False:
            return None

        if role not in (qt.Qt.DisplayRole, qt.Qt.ToolTipRole):
            return None

        obs = list(self.observations.keys())[index.row()]
        if index.column() == 0:
            if role == qt.Qt.ToolTipRole:
                return obs
            elif isinstance(obs, (TomwerScanBase, BlissScan)):
                return str(obs)
            else:
                return os.path.basename(obs)
        elif index.column() == 1:
            return self.observations[obs]
        elif index.column() == 2:
            if isinstance(obs, TomwerScanBase):
                return obs.tomo_n or 0
            elif isinstance(obs, BlissScan):
                return "(at least) {} over {}".format(
                    obs.n_acquired or "?", obs.tomo_n or "?"
                )
            elif HDF5TomoScan.directory_contains_scan(directory=obs):
                scan = HDF5TomoScan(scan=obs)
                return str(len(scan.projections))
            elif os.path.exists(obs) and os.path.isdir(obs):
                return str(len(os.listdir(obs)))
            else:
                return None
        elif index.column() == 3:
            if isinstance(obs, TomwerScanBase):
                return obs.type
            elif isinstance(obs, BlissScan):
                return "hdf5"
            elif HDF5TomoScan.directory_contains_scan(directory=obs):
                return "hdf5"
            else:
                return "edf"
        else:
            return None

    def headerData(self, col, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            return self.header[col]
        return None
