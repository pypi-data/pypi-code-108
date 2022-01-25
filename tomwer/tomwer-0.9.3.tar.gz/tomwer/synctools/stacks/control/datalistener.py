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
__date__ = "16/11/2020"


from silx.gui import qt
from tomwer.core.process.control.datalistener import DataListener
from ..processingstack import FIFO, ProcessingThread
from tomwer.core.scan.blissscan import BlissScan

try:
    # new HDF5Config class
    from nxtomomill.io.config import TomoHDF5Config as HDF5Config
except ImportError:
    from nxtomomill.io.config import HDF5Config
import logging

_logger = logging.getLogger(__name__)


class DataListenerProcessStack(FIFO, qt.QObject):
    """Stack of file conversion once received by the data-listener
    from a bliss file and a specific entry"""

    def __init__(self, parent=None):
        qt.QObject.__init__(self, parent=parent)
        FIFO.__init__(self, process_id=-1)
        self._results = {}

    def _process(self, scan, configuration, callback=None):
        assert isinstance(scan, BlissScan)
        assert isinstance(configuration, HDF5Config)
        _logger.info("DataListenerProcessStack is processing {}".format(str(scan)))
        self._scan_currently_computed = scan
        self._computationThread.finished.connect(self._end_threaded_computation)

        self._computationThread.init(scan=scan, configuration=configuration)
        # need to manage connect before starting it because
        self._computationThread.start()

    def _end_threaded_computation(self, callback=None):
        self._computationThread.finished.disconnect(self._end_threaded_computation)
        super()._end_threaded_computation(callback=callback)

    def _create_processing_thread(self, process_id=None) -> qt.QThread:
        thread = _DataListenerConverterThread()
        thread.setParent(self)
        return thread

    def _end_computation(self, scan, future_scan, callback):
        """
        callback when the computation thread is finished

        :param scan: pass if no call to '_computationThread is made'
        """
        if callback is not None:
            callback()
        if scan in self._results:
            nx_scan = self._results[scan]
            del self._results[scan]
        else:
            nx_scan = None
        self.sigComputationEnded.emit(nx_scan, None)
        self._processing = False
        if self.can_process_next():
            self._process_next()

    def register_result(self, bliss_scan, nx_scan):
        self._results[bliss_scan] = nx_scan


class _DataListenerConverterThread(ProcessingThread):
    """
    Thread use to execute the processing of nxtomomill
    """

    def __init__(self):
        ProcessingThread.__init__(self)
        self._scan = None
        self._configuration = None

    def init(self, scan, configuration):
        if not isinstance(scan, BlissScan):
            raise TypeError(
                "Only manage BlissScan. {} is not managed" "".format(type(scan))
            )
        assert isinstance(configuration, HDF5Config)
        self._scan = scan
        self._configuration = configuration

    def run(self):
        self.sigComputationStarted.emit()
        _logger.processStarted(
            "Start conversion of bliss scan {}".format(str(self._scan))
        )

        data_listener = DataListener()
        data_listener.set_configuration(self._configuration or {})
        try:
            scans = data_listener.process_sample_file(
                sample_file=self._scan.master_file,
                entry=self._scan.entry,
                proposal_file=self._scan.proposal_file,
                master_sample_file=self._scan.saving_file,
            )
        except Exception as e:
            _logger.processFailed(
                "Conversion of bliss scan {}." "Reason is {}".format(str(self._scan), e)
            )
            scans = None
        else:
            _logger.processSucceed(
                "Conversion of bliss scan {}." "".format(str(self._scan))
            )
        self.parent().register_result(self._scan, scans)
