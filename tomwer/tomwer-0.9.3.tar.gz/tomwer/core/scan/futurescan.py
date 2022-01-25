# coding: utf-8
# /*##########################################################################
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
#############################################################################*/


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/10/2021"


import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from typing import Optional
from typing import Iterable
from typing import Union
import datetime

_logger = logging.getLogger(__name__)


class FutureTomwerScan:
    """Container for an existing TomwerScanBase with some future object
    (like slice reconstruction on slurm...)

    :param TomwerScanBase scan: scan at the origin of the FutureTomwerScan
    :param tuple futures: tuple of Future (dask.distributed)
    :param start_time: start_time of the FutureTomwerScan. If not provided
                       this will be set to the date of creation of the object.
    :type start_time: Optional[datetime.time]
    :param Iterable clients: list of daks.distributed.client used to do future
                             computation
    :param int process_requester_id: process of the id requesting future
                                     processing. This is usefull to keep a trace on
                                     the source of the computation. To display
                                     supervisor 'request' for example.
    """

    def __init__(
        self,
        scan: TomwerScanBase,
        futures: Optional[Union[tuple, list]],
        start_time: Optional[datetime.time] = None,
        clients: Optional[Iterable] = None,
        process_requester_id: Optional[int] = None,
    ):
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(
                f"scan is expected to be an instance of {TomwerScanBase} not {type(scan)}"
            )
        self._scan = scan
        self._start_time = (
            start_time if start_time is not None else datetime.datetime.now()
        )
        self._process_requester_id = process_requester_id
        # handle futures
        if futures is None:
            self._futures = None
        elif not isinstance(futures, (tuple, list)):
            raise TypeError(
                f"futures is expected to be a tuple or a list not {type(futures)}"
            )
        else:
            self._futures = list(futures)
        # handle clients
        if clients is None:
            self._clients = None
        elif not isinstance(clients, (tuple, list)):
            raise TypeError(
                f"clients is expected to be a tuple or a list not {type(clients)}"
            )
        else:
            self._clients = list(clients)

    @property
    def status(self) -> Optional[str]:
        def future_status(future):

            if future.cancelled():
                return "cancelled"
            elif not future.done():
                return "running"
            elif future.exception() is not None:
                return "error"
            else:
                return "finished"

        all_status = [future_status(fut) for fut in self._futures]
        # small hack to get a common status for a list of future.
        # if at least one running we can wait for all to be processed
        # Then after this condition it means all jobs are finished
        # and we can check if there is an error
        # otherwise everything is "green"
        for status in ("pending", "running", "error", "cancelled", "finished"):
            if status in all_status:
                return status
        return None

    @property
    def start_time(self) -> Optional[datetime.time]:
        return self._start_time

    @property
    def scan(self) -> TomwerScanBase:
        # TODO: replace the scan by the DatasetIdentifier
        return self._scan

    @property
    def futures(self) -> Optional[tuple]:
        if self._futures is None:
            return None
        else:
            return tuple(self._futures)

    def extend_futures(self, futures: Iterable) -> None:
        if not isinstance(futures, Iterable):
            raise TypeError(f"futures should be an Iterable not {type(futures)}")
        if self._futures is None:
            self._futures = []
        self._futures.extend(futures)

    @property
    def clients(self) -> Optional[tuple]:
        if self._clients is None:
            return None
        else:
            return tuple(self._clients)

    def extend_clients(self, clients: Iterable) -> None:
        if not isinstance(clients, Iterable):
            raise TypeError(f"clients should be an Iterable not {type(clients)}")
        if self._clients is None:
            self._clients = []
        self._clients.extend(clients)

    @property
    def process_requester_id(self) -> Optional[int]:
        return self._process_requester_id

    def clear_clients(self):
        if self._clients is None:
            return
        for client in self._clients:
            try:
                client.close()
                client.cluster.close()
            except Exception as e:
                _logger.warning(e)
        self._clients = None

    def results(self) -> TomwerScanBase:
        """Force future and callback synchronization"""
        results = []
        [results.append(fut.result()) for fut in self._futures]
        return results

    def cancelled(self):
        cancelled = False
        for future in self.futures:
            cancelled = cancelled and future.cancelled()
        return cancelled

    def done(self):
        done = True
        for future in self.futures:
            done = done and future.done()
        return done

    def exceptions(self) -> Optional[dict]:
        """
        Return exception with future as key and exception as value
        """
        exceptions = {}
        for future in self.futures:
            if future.exception():
                exceptions[future] = future.exception()

        if len(exceptions) == 0:
            return None
        else:
            return exceptions

    def cancel(self):
        for future in self.futures:
            future.cancel()
        self.clear_clients()
