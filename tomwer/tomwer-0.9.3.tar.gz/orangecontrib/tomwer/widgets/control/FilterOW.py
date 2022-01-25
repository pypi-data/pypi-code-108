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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "19/07/2018"

from silx.gui import qt
from orangewidget import gui

import tomwer.core.process.conditions.filters
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from orangewidget.widget import Input, Output
from tomwer.web.client import OWClient
from tomwer.gui.conditions.filter import FileNameFilterWidget
from tomwer.core.scan.scanbase import TomwerScanBase
from processview.core.manager import DatasetState
from tomwer.utils import docstring
from tomwer.core.process.conditions import filters
import logging

logger = logging.getLogger(__name__)


class NameFilterOW(SuperviseOW, OWClient):
    name = "scan filter"
    id = "orange.widgets.tomwer.filterow"
    description = (
        "Simple widget which filter some data directory if the name"
        "doesn't match with the pattern defined."
    )
    icon = "icons/namefilter.svg"
    priority = 106
    keywords = ["tomography", "selection", "tomwer", "folder", "filter"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    ewokstaskclass = tomwer.core.process.conditions.filters.FileNameFilter

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        """ """
        SuperviseOW.__init__(self, parent)
        OWClient.__init__(self)

        self.widget = FileNameFilterWidget(parent=self)
        self.widget.setContentsMargins(0, 0, 0, 0)

        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self.widget)
        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        layout.addWidget(spacer)

    @Inputs.data
    def applyfilter(self, scan):
        if scan is None:
            return
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(f"{scan} is expected to be an instance of {TomwerScanBase}")

        process = filters.FileNameFilter(
            inputs={
                "data": scan,
                "pattern": self.getPattern(),
                "filter_type": self.getActiveFilter(),
                "invert_result": self.invertFilterAction(),
            }
        )
        process.run()
        out = process.outputs.data
        if out is not None:
            self.set_dataset_state(dataset=scan, state=DatasetState.SUCCEED)
            logger.processSucceed("{} pass through filter".format(str(scan)))
            self._signalScanReady(scan)
        else:
            self.set_dataset_state(dataset=scan, state=DatasetState.FAILED)
            logger.processFailed("{} NOT pass through filter".format(str(scan)))

    @docstring(SuperviseOW)
    def reprocess(self, dataset):
        self.applyfilter(dataset)

    def _signalScanReady(self, scan):
        self.Outputs.data.send(scan)

    def getPattern(self):
        return self.widget.getPattern()

    def setPattern(self, pattern):
        self.widget.setPattern(pattern)

    def getActiveFilter(self):
        return self.widget.getActiveFilter()

    def setActiveFilter(self, filter):
        self.widget.setActiveFilter(filter)

    def invertFilterAction(self):
        return self.widget.invertFilterAction()
