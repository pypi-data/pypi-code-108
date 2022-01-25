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
__date__ = "25/05/2018"


from silx.gui import qt
from tomwer.gui.qfolderdialog import QScanDialog
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.control.datalist import GenericDataList
import logging

logger = logging.getLogger(__name__)


class ScanSelectorWidget(qt.QWidget):
    """Widget used to select a scan on a list"""

    sigSelectionChanged = qt.Signal(list)
    """Signal emitted when the selection changed"""

    sigUpdated = qt.Signal()
    """signal emitted when the scan list change"""

    def __init__(self, parent=None):
        def getAddAndRmButtons():
            lLayout = qt.QHBoxLayout()
            w = qt.QWidget(self)
            w.setLayout(lLayout)
            self._addButton = qt.QPushButton("Add")
            self._addButton.clicked.connect(self._callbackAddFolder)
            self._rmButton = qt.QPushButton("Remove")
            self._rmButton.clicked.connect(self._callbackRemoveFolder)

            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
            lLayout.addWidget(spacer)
            lLayout.addWidget(self._addButton)
            lLayout.addWidget(self._rmButton)

            return w

        def getSendButton():
            lLayout = qt.QHBoxLayout()
            widget = qt.QWidget(self)
            widget.setLayout(lLayout)
            self._sendButton = qt.QPushButton("Select")
            self._sendButton.clicked.connect(self._selectActiveScan)

            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
            lLayout.addWidget(spacer)
            lLayout.addWidget(self._sendButton)

            return widget

        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.dataList = GenericDataList(parent=self)
        self.dataList.setSelectionMode(qt.QAbstractItemView.ExtendedSelection)
        self.layout().addWidget(self.dataList)
        self.layout().addWidget(getAddAndRmButtons())
        self.layout().addWidget(getSendButton())
        self.setAcceptDrops(True)

    def add(self, scan):
        self.dataList.add(scan)
        self.sigUpdated.emit()

    def remove(self, scan):
        self.dataList.remove(scan)
        self.sigUpdated.emit()

    def n_scan(self) -> int:
        return len(self.dataList.items)

    def selectAll(self):
        self.dataList.selectAll()

    def _callbackAddFolder(self):
        """ """
        dialog = QScanDialog(self, multiSelection=True)

        if not dialog.exec_():
            dialog.close()
            return

        for folder in dialog.files_selected():
            self.add(folder)
        self.sigUpdated.emit()

    def _selectActiveScan(self):
        sItem = self.dataList.selectedItems()
        if sItem and len(sItem) >= 1:
            selection = [_item.text() for _item in sItem]
            self.sigSelectionChanged.emit(list(selection))
        else:
            logger.warning("No active scan detected")

    def _callbackRemoveFolder(self):
        """ """
        selectedItems = self.dataList.selectedItems()
        if selectedItems is not None:
            for item in selectedItems:
                self.dataList.remove_item(item)
        self.sigUpdated.emit()

    def setActiveScan(self, scan):
        """
        set the given scan as the active one

        :param scan: the scan to set active
        :type scan: Union[str, TomoBase]
        """
        scanID = scan
        if isinstance(scan, TomwerScanBase):
            scanID = scan.path
        self.dataList.setCurrentItem(self.dataList.items[scanID])
