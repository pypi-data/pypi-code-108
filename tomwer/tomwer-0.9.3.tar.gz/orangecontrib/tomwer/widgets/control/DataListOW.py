# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2021 European Synchrotron Radiation Facility
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
__date__ = "01/12/2016"

from orangewidget import widget, gui
from tomwer.core.utils import logconfig
from tomwer.gui.control.datalist import GenericDataListDialog
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.web.client import OWClient
from tomwer.core.scan.scanbase import TomwerScanBase
import tomwer.core.process.control.scanlist
from orangewidget.settings import Setting
from orangewidget.widget import Output, Input, OWBaseWidget
import logging

logger = logging.getLogger(__name__)


class DataListOW(OWBaseWidget, OWClient, openclass=True):
    name = "data list"
    id = "orange.widgets.tomwer.scanlist"
    description = "List path to reconstructions/scans. Those path will be send to the next box once validated."
    icon = "icons/scanlist.svg"
    priority = 50
    keywords = ["tomography", "file", "tomwer", "folder"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _scanIDs = Setting(list())

    ewokstaskclass = tomwer.core.process.control.scanlist._ScanListPlaceHolder

    class Outputs:
        data = Output(name="data", type=TomwerScanBase, doc="one scan to be process")

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        """A simple annuary which register all folder containing completed scan

        .. warning: the widget won't check for scan validity and will only
            emit the path to folders to the next widgets

        :param parent: the parent widget
        """
        widget.OWBaseWidget.__init__(self, parent)
        OWClient.__init__(self)
        self.widget = GenericDataListDialog(parent=self)
        self.widget.sigUpdated.connect(self._updateSettings)
        self._loadSettings()
        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self.widget)
        self.widget._sendButton.clicked.connect(self._sendList)

        # expose API
        self.n_scan = self.widget.n_scan

        # alias used for the 'simple workflow' for now
        self.start = self._sendList
        self.clear = self.widget.clear

    def _sendList(self):
        """Send a signal for each list to the next widget"""

        def send(scan_):
            mess = "sending one scan %s" % d
            logger.debug(
                mess,
                extra={
                    logconfig.DOC_TITLE: self.widget._scheme_title,
                    logconfig.SCAN_ID: str(scan_),
                },
            )
            self.Outputs.data.send(scan_)

        for d in self.widget.datalist.items:
            if d in self.widget.datalist._scanIDs:
                send(scan_=self.widget.datalist._scanIDs[d])
            else:
                logger.error("unable to retrieve scan {}".format(d))

    @Inputs.data
    def add(self, scan):
        if scan is None:
            return

        self.widget.add(scan)

    def _loadSettings(self):
        for scan in self._scanIDs:
            assert isinstance(scan, str)
            if "@" in scan:
                entry, file_path = scan.split("@")
                hdf5_tomo_scan = HDF5TomoScan(entry=entry, scan=file_path)
                self.add(hdf5_tomo_scan)
            else:
                self.add(scan)

    def _updateSettings(self):
        self._scanIDs = []
        for scan in self.widget.datalist.items:
            self._scanIDs.append(scan)
