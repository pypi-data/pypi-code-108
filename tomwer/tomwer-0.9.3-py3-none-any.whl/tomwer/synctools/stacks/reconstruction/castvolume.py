# coding: utf-8
###########################################################################
# Copyright (C) 2016-2019 European Synchrotron Radiation Facility
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

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "15/21/2021"


from tomwer.core.process.reconstruction.nabu.castvolume import CastVolumeTask
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.settings import get_lbsram_path, isOnLbsram
from tomwer.core.utils import isLowOnMemory
from ..processingstack import FIFO, ProcessingThread
from processview.core.superviseprocess import SuperviseProcess
from processview.core.manager import ProcessManager, DatasetState
from silx.gui import qt
import logging
import functools

_logger = logging.getLogger(__name__)


class CastVolumeProcessStack(FIFO, qt.QObject):
    def __init__(self, process_id=None):
        qt.QObject.__init__(self)
        FIFO.__init__(self, process_id=process_id)
        self._dry_run = False

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    def _process(self, scan, configuration, callback=None):
        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.ON_GOING,
        )
        _logger.processStarted(f"start cast volume to {configuration} {str(scan)}")
        assert isinstance(scan, TomwerScanBase)

        if isOnLbsram(scan) and isLowOnMemory(get_lbsram_path()) is True:
            # if computer is running into low memory on lbsram skip it
            mess = "low memory, skip volume cast", scan.path
            ProcessManager().notify_dataset_state(
                dataset=scan, process=self._process_id, state=DatasetState.SKIPPED
            )
            _logger.processSkipped(mess)
            if callback is not None:
                callback()
            self.scan_ready(scan=scan)
        else:
            self._scan_currently_computed = scan
            self._computationThread.init(scan=scan, configuration=configuration)
            # need to manage connect before starting it because
            fct_callback = functools.partial(self._end_threaded_computation, callback)
            self._computationThread.finished.connect(fct_callback)
            self._computationThread.start()

    def _end_computation(self, scan, future_scan, callback):
        """
        callback when the computation thread is finished

        :param scan: pass if no call to '_computationThread is made'
        """
        assert isinstance(scan, TomwerScanBase)
        FIFO._end_computation(
            self, scan=scan, future_scan=future_scan, callback=callback
        )

    def _end_threaded_computation(self, callback=None):
        assert self._scan_currently_computed is not None
        self._computationThread.finished.disconnect()
        if callback:
            callback()
        FIFO._end_threaded_computation(self)

    def _create_processing_thread(self, process_id=None) -> qt.QThread:
        return _ProcessingThread(process_id=process_id)


class _ProcessingThread(ProcessingThread, SuperviseProcess):
    """
    Thread use to execute the processing of the axis position
    """

    def __init__(self, process_id=None):
        SuperviseProcess.__init__(self, process_id=process_id)
        try:
            ProcessingThread.__init__(self, process_id=process_id)
        except TypeError:
            ProcessingThread.__init__(self)
        self._dry_run = False
        self._scan = None
        self._configuration = None

    def set_dry_run(self, dry_run):
        self._dry_run = dry_run

    def init(self, scan, configuration):
        self._scan = scan
        self._configuration = configuration

    def run(self):
        self.sigComputationStarted.emit()
        castVolume = CastVolumeTask(
            process_id=self.process_id,
            varinfo=None,
            inputs={
                "data": self._scan,
                "configuration": self._configuration,
            },
        )
        try:
            castVolume.run()
        except Exception as e:
            raise e
            _logger.error(str(e))
            details = f"Volume cast of {str(self._scan)} failed. {str(e)}"
            state = DatasetState.FAILED
        else:
            details = f"Volume cast of {str(self._scan)} succeed."
            state = DatasetState.SUCCEED
        finally:
            ProcessManager().notify_dataset_state(
                dataset=self._scan,
                process=self,
                state=state,
                details=details,
            )
