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
from orangewidget.settings import Setting
from orangewidget.widget import Input, Output

import tomwer.core.process.control.timer
from tomwer.core.scan.scanbase import TomwerScanBase
from processview.core.manager import ProcessManager, DatasetState
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from tomwer.utils import docstring
import logging
import functools

_logger = logging.getLogger(__name__)


class _TimerWidget(qt.QWidget):
    def __init__(self, parent, _time=None):
        if _time is not None:
            assert type(_time) is int
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        self.layout().addWidget(qt.QLabel("time to wait (in sec):", parent=self), 0, 0)
        self._timeLE = qt.QSpinBox(parent=self)
        self._timeLE.setMinimum(0)
        self._timeLE.setValue(_time or 1)
        self.layout().addWidget(self._timeLE, 0, 1)

        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 1, 0)

        # expose API
        self.timeChanged = self._timeLE.valueChanged


class TimerOW(SuperviseOW):
    name = "timer"
    id = "orange.widgets.tomwer.filterow"
    description = (
        "Simple widget which wait for a defined amont of time and" "release the data"
    )
    icon = "icons/time.png"
    priority = 200
    keywords = ["control", "timer", "wait", "data"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False
    _waiting_time = Setting(int(1))

    ewokstaskclass = tomwer.core.process.control.timer.Timer

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        """ """
        SuperviseOW.__init__(self, parent)
        self._widget = _TimerWidget(parent=self, _time=self._waiting_time)
        self._widget.setContentsMargins(0, 0, 0, 0)

        layout = gui.vBox(self.mainArea, self.name).layout()
        layout.addWidget(self._widget)

        self._widget.timeChanged.connect(self._updateTime)

    @Inputs.data
    def process(self, scan):
        if scan is None:
            return

        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.ON_GOING,
        )

        callback = functools.partial(self._get_out, scan)
        _timer = qt.QTimer(self)
        _timer.singleShot(self._waiting_time * 1000, callback)

    def _updateTime(self, newTime):
        self._waiting_time = newTime

    def _get_out(self, scan):
        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.SUCCEED,
        )
        self.Outputs.data.send(scan)

    @docstring(SuperviseOW)
    def reprocess(self, dataset):
        self.process(dataset)
