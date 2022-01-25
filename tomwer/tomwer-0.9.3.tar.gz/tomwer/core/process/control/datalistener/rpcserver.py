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
__date__ = "09/06/2020"

import time
import logging
import threading
import typing
from silx.utils.enum import Enum as _Enum
from multiprocessing import Process
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
import socket
from psutil import process_iter
import getpass


_logger = logging.getLogger(__name__)


class TangoAcquisitionStatus(_Enum):
    """list of possible status of the acquisition"""

    STARTED = "started"
    ON_GOING = "on going"
    CANCELED = "canceled"
    ENDED = "ended"


class _TangoState:
    MOVING = "moving"
    ON = "on"
    FAULT = "fault"


class BlissAcquisition:
    """Define an acquisition made with bliss / tango"""

    def __init__(self, file_path, entry_name, proposal_file, sample_file, start_time):
        self.entry = entry_name
        self.master_file = file_path
        self.proposal_file = proposal_file
        self.sample_file = sample_file
        self.scan_numbers = []
        self.status = BlissAcquisition
        self._start_time = start_time
        self._end_time = None
        self._error = None
        self._state = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    def add_scan_number(self, scan_number):
        self.scan_numbers.append(scan_number)

    def set_status(self, status):
        self.status = TangoAcquisitionStatus.from_value(status)

    def end(self, end_time, succeed: bool, error: typing.Union[None, str]):
        if succeed is True:
            self.status = TangoAcquisitionStatus.ENDED
        else:
            self.status = TangoAcquisitionStatus.CANCELED
        self._error = error
        self._end_time = end_time

    @property
    def has_error(self):
        return self._error is not None

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def error(self) -> typing.Union[None, str]:
        return self.error


class _BaseDataListenerThread:
    """Base class for data listener thread. Thread can be a threading.Thread
    or a qt.QThread.

    On the current bliss system (2020) a sequence is an acquisition. A sequence
    is composed of several scans. A scan can be the 'init' information,
    dark frames, flat frames, projections frames, return projections...

    :param str device_name: name of the tango device proxy
    :param Union[None, list]: list of the tango acquisitions
    """

    _JOIN_TIMEOUT = 5  # s

    def __init__(self, host, port, acquisitions=None):
        assert host is not None
        assert port is not None
        # connect to the tango device
        self.acquisitions = acquisitions or []
        """acquisition with scan information, as key and acquisition status
        as value"""
        self._host = host
        # if host is None then use hostname
        if self._host is None:
            self._host = socket.gethostname()
        self._port = port
        self._tomo_state = None
        # state of the current sequence
        self._current_sequence = None
        # current sequence
        self._current_scan_number = None
        # scan of the sequence currently recording
        self._server = None
        self._stop = False

    def _rpc_sequence_started(
        self, saving_file, scan_title, sequence_scan_number, proposal_file, sample_file
    ):

        self._current_sequence = BlissAcquisition(
            file_path=saving_file,
            entry_name=sequence_scan_number,
            proposal_file=proposal_file,
            start_time=time.ctime(),
            sample_file=sample_file,
        )
        self.sequence_started(acquisition=self._current_sequence)

    def sequence_started(self, acquisition: BlissAcquisition):
        print(
            "sequence {}@{} started. Title is {}, proposal file {}"
            "".format(
                acquisition.entry,
                acquisition.master_file,
                acquisition.title,
                acquisition.proposal_file,
            )
        )

    def _rpc_scan_started(self, scan_number):
        if self._current_sequence is not None:
            self._current_sequence.add_scan_number(scan_number=scan_number)
            self.scan_added(acquisition=self._current_sequence, scan_number=scan_number)

    def scan_added(self, acquisition: BlissAcquisition, scan_number: int):
        print("scan {} started".format(scan_number))

    def _rpc_scan_ended(self, scan_number):
        if self._current_sequence is not None:
            self.scan_ended(acquisition=self._current_sequence, scan_number=scan_number)

    def scan_ended(self, acquisition: BlissAcquisition, scan_number):
        print("scan {} ended".format(scan_number))

    def _rpc_sequence_ended(self, saving_file, sequence_scan_number, success):
        if success is False:
            _logger.warning(
                "sequence {}@{} failed".format(sequence_scan_number, saving_file)
            )
            if self._current_sequence is not None:
                try:
                    self.sequence_failed(self._current_sequence)
                except Exception as e:
                    _logger.warning("Fail to catch cancel scan. error is", e)

            return

        if self._current_sequence is not None:
            if (
                self._current_sequence.master_file == saving_file
                and self._current_sequence.entry == sequence_scan_number
            ):
                self.sequence_ended(self._current_sequence)
            else:
                name = "@".join((sequence_scan_number, saving_file))
                name_current = "@".join(
                    (self._current_sequence.entry, self._current_sequence.master_file)
                )

                _logger.warning(
                    "End of {} detected but does not fit the "
                    "current acquisition {}".format(name, name_current)
                )

    def sequence_ended(self, acquisition: BlissAcquisition):
        """callback when a sequence end (with success)"""
        print(
            "sequence {}@{} ended. Succeed: {}".format(
                acquisition.entry, acquisition.master_file, acquisition.status
            )
        )

    def sequence_failed(self, acquisition: BlissAcquisition):
        """callback when a sequence fails (probably canceled)"""
        print(
            "sequence {}@{} failed".format(acquisition.entry, acquisition.master_file)
        )

    @Request.application
    def application(self, request):
        dispatcher["scan_started"] = self._rpc_scan_started
        dispatcher["scan_ended"] = self._rpc_scan_ended
        dispatcher["sequence_started"] = self._rpc_sequence_started
        dispatcher["sequence_ended"] = self._rpc_sequence_ended

        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype="application/json")

    def start(self) -> None:
        self._stop = False
        _logger.info("launch rpc server on {}:{}".format(self._host, self._port))
        self._server = Process(
            target=run_simple, args=(self._host, self._port, self.application)
        )
        self._server.start()
        _logger.info("launcher server with pid {}".format(self._server.pid))

    def stop(self):
        self._stop = True
        if self._server is not None:
            _logger.info("stop rpc server on {}:{}".format(self._host, self._port))
            self._server.terminate()
            self._server.join(_BaseDataListenerThread._JOIN_TIMEOUT)
            self._server = None


class DataListenerThread(_BaseDataListenerThread, threading.Thread):
    """Implementation of _BaseDataListenerThread with a threading.Thread"""

    def __init__(self, host, port, acquisitions=None):
        threading.Thread.__init__(self)
        _BaseDataListenerThread.__init__(
            self, host=host, port=port, acquisitions=acquisitions
        )


def send_signal_to_local_rpc_servers(signal, port, extended_find=True):
    """ "
    :param signal: signal to be emit
    :param int port: port to check
    :param bool extended_find: if True then will try to find a process that
                               occupy the port even if this is not a process
                               launched by the user and launched by tomwer.
    """
    # TODO: this should be moved to some utils
    import psutil

    found = False
    for proc in process_iter():
        # try to find a process we can handle
        if proc.username() == getpass.getuser():
            try:
                for conns in proc.connections():
                    # make sure we will kill the correct process
                    if conns.laddr.port == port and proc.name() in (
                        "tomwer",
                        "orange-canvas",
                    ):
                        _logger.warning(
                            "send {} signal to pid {}" "".format(signal, proc.pid)
                        )
                        proc.send_signal(signal)
                        found = True
                        return
            except (psutil.PermissionError, psutil.AccessDenied):
                pass
    if not extended_find:
        return
    # if process not found try to find one to inform the user
    if not found:
        for proc in process_iter():
            try:
                for conns in proc.connections():
                    # make sure we will kill the correct process
                    if conns.laddr.port == port:
                        _logger.warning(
                            "process pid: {} - {} seems to be one occupying port {}"
                            "".format(proc.pid, proc.name(), port)
                        )
                        return
            except (psutil.PermissionError, psutil.AccessDenied):
                pass


if __name__ == "__main__":
    worker = _BaseDataListenerThread(host="localhost", port=4000)
    worker.run()
    time.sleep(20)
    worker.stop()
    exit(0)
