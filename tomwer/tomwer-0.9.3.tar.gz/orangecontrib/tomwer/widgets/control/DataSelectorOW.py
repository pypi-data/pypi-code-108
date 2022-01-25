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

from orangewidget import gui
from orangewidget.widget import Output, Input, OWBaseWidget
from tomwer.web.client import OWClient
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.gui.scanselectorwidget import ScanSelectorWidget
from tomwer.core.scan.scanbase import TomwerScanBase
from orangewidget.settings import Setting
import tomwer.core.process.control.scanvalidator
import logging

logger = logging.getLogger(__name__)


class DataSelectorOW(OWBaseWidget, OWClient, openclass=True):
    name = "data selector"
    id = "orange.widgets.tomwer.scanselector"
    description = (
        "List all received scan. Then user can select a specific"
        "scan to be passed to the next widget."
    )
    icon = "icons/scanselector.svg"
    priority = 42
    keywords = ["tomography", "selection", "tomwer", "folder"]

    ewokstaskclass = tomwer.core.process.control.scanvalidator._ScanValidatorPlaceHolder

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _scanIDs = Setting(list())

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        """ """
        OWBaseWidget.__init__(self, parent)
        OWClient.__init__(self)

        self.widget = ScanSelectorWidget(parent=self)
        self._loadSettings()

        self.widget.sigUpdated.connect(self._updateSettings)
        self.widget.sigSelectionChanged.connect(self.changeSelection)
        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self.widget)
        # expose API
        self.setActiveScan = self.widget.setActiveScan
        self.selectAll = self.widget.selectAll
        self.n_scan = self.widget.n_scan
        self.add = self.widget.add

    @Inputs.data
    def addScan(self, scan):
        if scan is not None:
            self.widget.add(scan)

    def changeSelection(self, list_scan):
        if list_scan:
            for scan_id in list_scan:
                if scan_id in self.widget.dataList._scanIDs:
                    scan = self.widget.dataList._scanIDs[scan_id]
                    assert isinstance(scan, TomwerScanBase)
                    self.Outputs.data.send(scan)
                else:
                    logger.error("%s not found in scan ids" % scan_id)

    def send(self):
        """send output signals for each selected items"""
        sItem = self.widget.dataList.selectedItems()
        if sItem and len(sItem) >= 1:
            selection = [_item.text() for _item in sItem]
            self.changeSelection(list_scan=selection)

    def _loadSettings(self):
        for scan in self._scanIDs:
            assert isinstance(scan, str)
            if "@" in scan:
                entry, file_path = scan.split("@")
                hdf5_tomo_scan = HDF5TomoScan(entry=entry, scan=file_path)
                self.addScan(hdf5_tomo_scan)
            else:
                self.addScan(scan)

    def _updateSettings(self):
        self._scanIDs = []
        for scan in self.widget.dataList.items:
            self._scanIDs.append(scan)
