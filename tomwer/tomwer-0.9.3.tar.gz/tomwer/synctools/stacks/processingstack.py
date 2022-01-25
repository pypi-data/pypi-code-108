# coding: utf-8
###########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
#############################################################################
"""Define some processing stack"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "08/01/2020"


from queue import Queue
from silx.gui import qt
from processview.core.manager import ProcessManager, DatasetState
from processview.core.superviseprocess import SuperviseProcess


class ProcessingThread(qt.QThread):
    """Class for running some processing"""

    sigComputationStarted = qt.Signal()
    """Signal emitted when a computation is started"""


class FIFO(Queue, SuperviseProcess):
    """Processing Queue with a First In, First Out behavior"""

    sigComputationStarted = qt.Signal(object)
    """Signal emitted when a computation is started"""
    sigComputationEnded = qt.Signal(object, object)
    """Signal emitted when a computation is ended. First parameter is mandatory and
    is the scan computed. Second one is an optional FutureTomwerScan"""

    def __init__(self, process_id=None):
        SuperviseProcess.__init__(self, process_id=process_id)
        Queue.__init__(self)
        self._computationThread = self._create_processing_thread(process_id=process_id)
        assert isinstance(self._computationThread, ProcessingThread)
        self._computationThread.sigComputationStarted.connect(
            self._start_threaded_computation
        )
        """scan process by the thread"""
        self._scan_currently_computed = None
        """Scan computed currently"""
        self._processing = False

    def add(self, scan, configuration=None, callback=None):
        """
        add a scan to process

        :param TomwerScanBase scan: scan to process
        :param configuration: configuration of the process
        :param callback: function to call once the processing is Done
        """
        try:
            if self.process_id not in (None, -1):
                ProcessManager().notify_dataset_state(
                    dataset=scan,
                    process=self,
                    state=DatasetState.PENDING,
                )
        except Exception:
            pass
        Queue.put(self, (scan, configuration, callback))
        if self.can_process_next():
            self._process_next()

    def _process(self, scan, configuration, callback):
        raise NotImplementedError("Virtual class")

    def _process_next(self):
        if Queue.empty(self):
            return

        self._processing = True
        scan, configuration, callback = Queue.get(self)
        self._process(scan=scan, configuration=configuration or {}, callback=callback)

    def can_process_next(self):
        """
        :return: True if the computation thread is ready to compute
        a new axis position
        :rtype: bool
        """
        return not self._processing

    def _end_computation(self, scan, future_scan, callback):
        """
        callback when the computation thread is finished

        :param scan: pass if no call to '_computationThread is made'
        """
        if callback is not None:
            callback()
        sender = self.sender()
        if hasattr(sender, "future_scan"):
            future_scan = sender.future_scan
        else:
            future_scan = None

        self.sigComputationEnded.emit(scan, future_scan)
        self._processing = False
        if self.can_process_next():
            self._process_next()

    def _create_processing_thread(self, process_id=None) -> ProcessingThread:
        raise NotImplementedError("Virtual class")

    def is_computing(self):
        """Return True if processing thread is running (mean that computation
        is on going)"""
        return self._processing

    def wait_computation_finished(self):
        """
        Wait until the computation is finished
        """
        if self._processing:
            self._computationThread.wait()

    def _start_threaded_computation(self, *args, **kwargs):
        self.sigComputationStarted.emit(self._scan_currently_computed)

    def _end_threaded_computation(self, callback=None):
        sender = self.sender()
        if hasattr(sender, "future_scan"):
            future_scan = sender.future_scan
        else:
            future_scan = None
        self._end_computation(
            scan=self._scan_currently_computed,
            callback=callback,
            future_scan=future_scan,
        )

    def stop(self):
        while not self.empty():
            self.get()
        self._computationThread.blockSignals(True)
        self._computationThread.wait()
