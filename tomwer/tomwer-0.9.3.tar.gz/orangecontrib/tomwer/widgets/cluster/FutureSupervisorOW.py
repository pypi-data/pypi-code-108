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
__date__ = "14/10/2021"


from orangewidget import gui
from orangewidget.widget import Input, Output
from orangewidget.widget import OWBaseWidget
from orangewidget.settings import Setting
from silx.gui import qt
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.futurescan import FutureTomwerScan
from tomwer.gui.cluster.supervisor import (
    FutureTomwerScanObserverWidget as _FutureTomwerScanObserverWidget,
)
from processview.core.superviseprocess import SuperviseProcess
from processview.core.manager import ProcessManager, DatasetState
from silx.gui.utils.concurrent import submitToQtMainThread
import time


class FutureSupervisorOW(OWBaseWidget, openclass=True):
    """
    Orange widget to define a slurm cluster as input of other
    widgets (based on nabu for now)
    """

    name = "future supervisor"
    id = "orange.widgets.tomwer.cluster.FutureSupervisorOW.FutureSupervisorOW"
    description = "Observe slurm job registered."
    icon = "icons/slurmobserver.svg"
    priority = 22
    keywords = [
        "tomography",
        "tomwer",
        "slurm",
        "observer",
        "cluster",
        "job",
        "sbatch",
        "supervisor",
        "future",
    ]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _static_input = Setting(dict())

    class Inputs:
        future_in = Input(
            name="future_data",
            type=FutureTomwerScan,
            doc="data with some remote processing",
            multiple=True,
            default=True,
        )

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        super().__init__(parent)
        # gui
        layout = gui.vBox(self.mainArea, self.name).layout()
        self._widget = FutureTomwerScanObserverWidget(
            parent=self, name=self.windowTitle()
        )
        layout.addWidget(self._widget)

        # connect signal / slot
        self._widget.observationTable.model().sigStatusUpdated.connect(
            self._convertBackAutomatically
        )
        self._widget.sigConversionRequested.connect(self._convertBack)

    def convertWhenFinished(self):
        return self._widget.convertWhenFinished()

    def _convertBackAutomatically(self, future_scan, status):
        if not isinstance(future_scan, FutureTomwerScan):
            raise TypeError(
                f"future_scan is expected to be an instance of {FutureTomwerScan} and not {type(future_scan)}"
            )
        if status == "finished" and self.convertWhenFinished():
            self._convertBack(future_scan)

    def _convertBack(self, future_scan):
        if not isinstance(future_scan, FutureTomwerScan):
            raise TypeError(
                f"future_scan is expected to be an instance of {FutureTomwerScan} and not {type(future_scan)}"
            )
        self._futureHasBeenConverted(future_scan, future_scan.scan)

    @Inputs.future_in
    def add(self, future_scan, signal_id=None):
        if future_scan is not None:
            self._widget.addFutureScan(future_scan=future_scan)

    def _futureHasBeenConverted(self, future_scan, scan):
        # clean client to free resources
        self._widget.removeFutureScan(future_scan=future_scan)
        future_scan.clear_clients()
        if scan is not None:
            self.Outputs.data.send(scan)


class FutureTomwerScanObserverWidget(_FutureTomwerScanObserverWidget, SuperviseProcess):
    """add dataset state notification (ProcessManager) to the original FutureTomwerScanObserverWidget"""

    REFRESH_FREQUENCE = 2
    """time between call to updateView"""

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self.name = name
        self._updateThread = _RefreshThread(
            callback=self.updateView, refresh_frequence=self.REFRESH_FREQUENCE
        )
        self.destroyed.connect(self.stopRefresh)
        self._updateThread.start()

    def stopRefresh(self):
        if self._updateThread is not None:
            self._updateThread.stop()
            self._updateThread.wait(self.REFRESH_FREQUENCE + 1)
            self._updateThread = None

    def close(self):
        self.stopRefresh()
        super().close()

    def addFutureScan(self, future_scan: FutureTomwerScan):
        super().addFutureScan(future_scan)
        self._updateScanSupervisor(future_scan)

    def removeFutureScan(self, future_scan: FutureTomwerScan):
        self._updateScanSupervisor(future_scan)
        super().removeFutureScan(future_scan)

    def _updateScanSupervisor(self, future_scan):
        r_id = future_scan.process_requester_id
        if r_id is not None:
            requester_name = ProcessManager().get_process(r_id).name
        else:
            requester_name = "unknow"
        details = f"job spawn by {requester_name}"
        if future_scan is None:
            return
        elif future_scan.status == "error":
            state = DatasetState.FAILED
            details = "\n".join([details, future_scan.exception()])
        elif future_scan.status == "pending":
            details = "\n".join([details, "pending"])
            state = DatasetState.PENDING
        elif future_scan.status == "finished":
            state = DatasetState.SUCCEED
        elif future_scan.status == "running":
            details = "\n".join([details, "running"])
            state = DatasetState.ON_GOING
        elif future_scan.status == "cancelled":
            details = "\n".join([details, "job cancelled"])
            state = DatasetState.SKIPPED
        elif future_scan.status is None:
            return
        else:
            raise ValueError(f"future scan status {future_scan.status} is not managed")
        ProcessManager().notify_dataset_state(
            dataset=future_scan.scan,
            process=self,
            state=state,
            details=details,
        )

    def _updateStatus(self, future_scan):
        self._updateScanSupervisor(future_scan)
        super()._updateStatus(future_scan)


class _RefreshThread(qt.QThread):
    """Simple thread to call a refresh callback each refresh_frequence (seconds)"""

    TIME_BETWEEN_LOOP = 0.5

    def __init__(self, callback, refresh_frequence) -> None:
        super().__init__()
        self._callback = callback
        self._refresh_frequence = refresh_frequence
        self._stop = False

    def stop(self):
        self._stop = True
        self._callback = None

    def run(self):
        w_t = self._refresh_frequence + self.TIME_BETWEEN_LOOP

        while not self._stop:
            if w_t <= 0:
                if self._callback is not None:
                    try:
                        submitToQtMainThread(self._callback)
                    except AttributeError:
                        # can happen when closing
                        pass
                w_t = self._refresh_frequence + self.TIME_BETWEEN_LOOP
            w_t -= self.TIME_BETWEEN_LOOP
            time.sleep(self.TIME_BETWEEN_LOOP)
