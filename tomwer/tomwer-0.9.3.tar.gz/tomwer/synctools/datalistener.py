# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
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
__date__ = "16/03/2020"


from tomwer.core.process.control.datalistener.rpcserver import _BaseDataListenerThread
from tomwer.core.process.control.datalistener.rpcserver import BlissAcquisition
from tomwer.core.process.control.datalistener.rpcserver import TangoAcquisitionStatus
from collections import namedtuple
from datetime import datetime
from silx.gui import qt
from tomwer.utils import docstring
import time
from multiprocessing import Manager, Lock
import logging

_logger = logging.getLogger(__name__)


class DataListenerQThread(_BaseDataListenerThread, qt.QThread):
    """Implementation of the _BaseDataListenerThread with a QThread.

    As jsonrpc is using gevent we want to limit the 'crossover' of gevent and
    qt. So the server is launch in another process and bot processes are
    sharing list of acquisitions (added, ended...).
    """

    sigAcquisitionStarted = qt.Signal(tuple)
    """Signal emitted when an acquisition is started. Tuple is:
    (master_file, master_entry)"""
    sigAcquisitionEnded = qt.Signal(tuple)
    """Signal emitted when an acquisition is ended. Tuple is
    (master_file, master_entry, succeed)"""
    sigScanAdded = qt.Signal(tuple)
    """Signal emitted when a scan is added to an acquisition. Tuple is
    (master_file, master_entry, scan_entry)"""
    sigServerStop = qt.Signal()
    """Signal if the rpc-server have been turn off"""

    _WAIT_BTW_COLLECT = 0.5

    def __init__(self, host, port, acquisitions):
        qt.QThread.__init__(self)
        _BaseDataListenerThread.__init__(
            self, host=host, port=port, acquisitions=acquisitions
        )
        self._manager = Manager()

        self._lock = Lock()
        self._sequence_started = self._manager.list()
        self._sequence_ended = self._manager.list()
        self._scan_added = self._manager.list()
        self._stop = False

    @docstring(_BaseDataListenerThread.sequence_started)
    def sequence_started(self, acquisition: BlissAcquisition) -> None:
        assert isinstance(acquisition, BlissAcquisition)
        with self._lock:
            self._sequence_started.append(
                (
                    acquisition.master_file,
                    acquisition.entry,
                    acquisition.proposal_file,
                    acquisition.sample_file,
                )
            )

    def _collect_sequence_started(self):
        with self._lock:
            for scan in self._sequence_started:
                master_file, entry, proposal_file, sample_file = scan
                self.sigAcquisitionStarted.emit(
                    (master_file, entry, proposal_file, sample_file)
                )

            self._sequence_started[:] = []

    @docstring(_BaseDataListenerThread.scan_added)
    def scan_added(self, acquisition: BlissAcquisition, scan_number: int) -> None:
        assert isinstance(acquisition, BlissAcquisition)
        with self._lock:
            self._scan_added.append(
                (
                    acquisition.master_file,
                    acquisition.entry,
                    acquisition.proposal_file,
                    acquisition.sample_file,
                    scan_number,
                )
            )

    def _collect_scan_added(self):
        with self._lock:
            for scan in self._scan_added:
                master_file, entry, proposal_file, sample_file, scan_number = scan
                self.sigScanAdded.emit(
                    (master_file, entry, proposal_file, sample_file, scan_number)
                )
            self._scan_added[:] = []

    @docstring(_BaseDataListenerThread.sequence_ended)
    def sequence_ended(self, acquisition: BlissAcquisition) -> None:
        assert isinstance(acquisition, BlissAcquisition)
        with self._lock:
            self._sequence_ended.append(
                (
                    acquisition.master_file,
                    acquisition.entry,
                    acquisition.proposal_file,
                    acquisition.sample_file,
                    not acquisition.has_error,
                )
            )

    def _collect_sequence_ended(self):
        with self._lock:
            for scan in self._sequence_ended:
                master_file, entry, proposal_file, sample_file, success = scan
                self.sigAcquisitionEnded.emit(
                    (master_file, entry, proposal_file, sample_file, success)
                )
            self._sequence_ended[:] = []

    @docstring(_BaseDataListenerThread.sequence_failed)
    def sequence_failed(self, acquisition: BlissAcquisition):
        assert isinstance(acquisition, BlissAcquisition)
        with self._lock:
            self._sequence_ended.append(
                (
                    acquisition.master_file,
                    acquisition.entry,
                    acquisition.proposal_file,
                    acquisition.sample_file,
                    False,
                )
            )

    def start(self):
        _BaseDataListenerThread.start(self)
        qt.QThread.start(self)

    def join(self, timeout=None):
        if timeout is None:
            self.wait()
        else:
            self.wait(timeout)

    def stop(self):
        _BaseDataListenerThread.stop(self)
        self._stop = True
        self.join()

    def _make_sure_server_still_running(self):
        if not self._server.is_alive():
            self.sigServerStop.emit()

    def run(self):
        while not self._stop:
            try:
                self._collect_sequence_started()
                self._collect_scan_added()
                self._collect_sequence_ended()
                self._make_sure_server_still_running()
            except Exception as e:
                _logger.error(e)
                break
            else:
                time.sleep(DataListenerQThread._WAIT_BTW_COLLECT)


_mock_acquisition_info = namedtuple(
    "_mock_acquisition_info", ["master_file", "entry", "scan_numbers", "waiting_time"]
)


class MockDataListenerQThread(DataListenerQThread):
    """
    Overwrite run() function and mock an acquisition for CI avoiding to have a
    tango server and tango install.
    """

    def __init__(self, host, port, acquisitions: list, mock_acquisitions: list):
        DataListenerQThread.__init__(
            self, host=host, port=port, acquisitions=acquisitions
        )
        assert isinstance(mock_acquisitions, (list, tuple))
        for acqui in mock_acquisitions:
            assert type(acqui) is _mock_acquisition_info
        self.mock_acquisitions = mock_acquisitions
        "waiting time between each scan / step of the acquisition"

    def get_device(self, device_name):
        return None

    def run(self) -> None:
        _logger.info("mock an acquisition using tango / tango")

        for mock_acqui in self.mock_acquisitions:
            if self._stop:
                return

            # first scan is the definition of the acquisition
            now = datetime.now()
            current_acquisition = BlissAcquisition(
                file_path=mock_acqui.master_file,
                entry_name=mock_acqui.entry,
                start_time=now.strftime("%H:%M:%S"),
                proposal_file=None,
                sample_file=None,
            )
            self.acquisitions.append(current_acquisition)
            self.sequence_started(current_acquisition)

            time.sleep(mock_acqui.waiting_time)

            # add scan numbers if any
            for scan_number in mock_acqui.scan_numbers:
                current_acquisition.add_scan_number(scan_number)
                current_acquisition.set_status(TangoAcquisitionStatus.ON_GOING)
                self.scan_added(
                    acquisition=current_acquisition, scan_number=scan_number
                )
                if self._stop:
                    return
                time.sleep(mock_acqui.waiting_time)

            # end acquisition
            now = datetime.now()
            current_acquisition.end(
                end_time=now.strftime("%H:%M:%S"), succeed=True, error=None
            )
            self._rpc_sequence_ended(acquisition=current_acquisition)
            time.sleep(mock_acqui.waiting_time)

        # wait until stop the thread
        while not self._stop:
            time.sleep(0.1)
