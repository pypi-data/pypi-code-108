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
__date__ = "18/02/2018"


from silx.gui import qt
from operator import itemgetter
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.scan.scanbase import TomwerScanBase


class ScanHistory(qt.QWidget):
    """Widget used to display the lastest discovered scans"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)

        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(qt.QLabel(""))

        self.scanHistory = qt.QTableView(parent=parent)
        self.scanHistory.setSelectionBehavior(qt.QAbstractItemView.SelectRows)
        self.scanHistory.setModel(
            _FoundScanModel(
                parent=self.scanHistory, header=("time", "type", "scan ID"), mlist={}
            )
        )
        self.scanHistory.resizeColumnsToContents()
        self.scanHistory.setSortingEnabled(True)
        self.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)

        self.layout().addWidget(self.scanHistory)
        header = self.scanHistory.horizontalHeader()
        if qt.qVersion() < "5.0":
            setResizeMode = header.setResizeMode
        else:
            setResizeMode = header.setSectionResizeMode
        setResizeMode(0, qt.QHeaderView.Fixed)
        setResizeMode(1, qt.QHeaderView.Fixed)
        setResizeMode(2, qt.QHeaderView.Stretch)
        header.setStretchLastSection(True)

    def update(self, scans):
        self.scanHistory.setModel(
            _FoundScanModel(
                parent=self, header=("time", "type", "scan ID"), mlist=scans
            )
        )
        self.scanHistory.resizeColumnsToContents()


class _FoundScanModel(qt.QAbstractTableModel):
    """
    Model for :class:_ScanHistory

    :param mlist: list of tuple (scan, time stamp)
    """

    def __init__(self, parent, header, mlist, *args):
        qt.QAbstractTableModel.__init__(self, parent, *args)
        self.header = header
        self.myList = mlist

    def rowCount(self, parent=None):
        if self.myList is None:
            return 0
        else:
            return len(self.myList)

    def columnCount(self, parent=None):
        return 3

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        if self.myList is None:
            return
        self.myList = sorted(list(self.myList), key=itemgetter(col))
        if order == qt.Qt.DescendingOrder:
            self.myList = list(reversed(sorted(list(self.myList), key=itemgetter(col))))

        self.layoutChanged.emit()

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != qt.Qt.DisplayRole:
            return None
        if index.column() == 0:
            return self.myList[index.row()][1].strftime("%a %m - %d - %Y   - %H:%M:%S")
        elif index.column() == 1:
            path = self.myList[index.row()][0]
            if isinstance(path, TomwerScanBase):
                return path.type
            elif HDF5TomoScan.directory_contains_scan(path) or "@" in path:
                return "hdf5"
            else:
                return "edf"
        elif index.column() == 2:
            return self.myList[index.row()][0]

    def headerData(self, col, orientation, role):
        if orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
            return self.header[col]
        return None
