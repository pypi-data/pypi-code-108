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
__date__ = "13/08/2021"

import shutil

from processview.core.manager import ProcessManager
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.settings import get_lbsram_path, isOnLbsram
from tomwer.core.utils import isLowOnMemory
from processview.core.manager import DatasetState
from ..processingstack import FIFO, ProcessingThread
from processview.core.superviseprocess import SuperviseProcess
from tomwer.core.process.reconstruction.darkref.darkrefscopy import DarkRefsCopy
from silx.gui import qt
import logging
import functools
import tempfile

_logger = logging.getLogger(__name__)


class DarkRefCopyProcessStack(FIFO, qt.QObject):
    """Implementation of the `.AxisProcess` but having a stack for treating
    scans and making computation in threads"""

    def __init__(self, process_id=None):
        self._save_dir = tempfile.mkdtemp()
        qt.QObject.__init__(self)
        FIFO.__init__(self, process_id=process_id)

    def __del__(self):
        try:
            shutil.rmtree(self._save_dir)
        except Exception as e:
            _logger.error(e)

    def _process(self, scan, configuration: dict, callback=None):
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(f"{scan} is expected to be an instance of {TomwerScanBase}")
        if not isinstance(configuration, dict):
            raise TypeError(f"{configuration} is expected to be an instance of {dict}")
        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.ON_GOING,
        )
        _logger.processStarted("dk-ref-copy {}" "".format(str(scan)))
        assert isinstance(scan, TomwerScanBase)
        self._scan_currently_computed = scan
        if isOnLbsram(scan) and isLowOnMemory(get_lbsram_path()) is True:
            # if computer is running into low memory on lbsram skip it
            mess = "low memory, skip dk-ref-copy", scan.path
            ProcessManager().notify_dataset_state(
                dataset=scan, process=self._process_id, state=DatasetState.SKIPPED
            )
            _logger.processSkipped(mess)
            if callback is not None:
                callback()
            self.scan_ready(scan=scan)
        else:
            self._scan_currently_computed = scan
            self._computationThread.init(scan=scan, inputs=configuration)
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
        return _ProcessingThread(process_id=process_id, save_dir=self._save_dir)


class _ProcessingThread(ProcessingThread, SuperviseProcess):
    """
    Thread use to execute the processing of the axis position
    """

    def __init__(self, save_dir, process_id=None):
        SuperviseProcess.__init__(self, process_id=process_id)
        try:
            ProcessingThread.__init__(self, process_id=process_id)
        except TypeError:
            ProcessingThread.__init__(self)
        self._save_dir = save_dir
        self._scan = None
        self._inputs = None

    def init(self, scan, inputs):
        self._scan = scan
        self._inputs = inputs

    def run(self):
        self.sigComputationStarted.emit()
        inputs = self._inputs
        inputs["data"] = self._scan
        inputs["save_dir"] = self._save_dir
        process = DarkRefsCopy(inputs=inputs, process_id=self.process_id)
        try:
            process.run()
        except Exception as e:
            _logger.warning(e)
