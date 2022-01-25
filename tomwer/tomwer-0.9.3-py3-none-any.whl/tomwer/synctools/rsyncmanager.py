# coding: utf-8
# /*##########################################################################
# Copyright (C) 2017 European Synchrotron Radiation Facility
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

"""
This module is used to manage the rsync between files for transfert.
"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "11/04/2017"


from rsyncmanager import RSyncManager
import time
from silx.gui import qt
import logging

logger = logging.getLogger(__name__)


class RSyncWorker(qt.QThread):
    """Thread which call for a synchronization on a folder each n seconds"""

    def __init__(self, src_dir, dst_dir, delta_time):
        qt.QThread.__init__(self)
        self._src_dir = src_dir
        self._dst_dir = dst_dir
        self._delta_tile = delta_time
        self._stop = False

    def stop(self):
        self._stop = True

    def _process_sync(self):
        RSyncManager().sync_file(
            source=self._src_dir, target=self._dst_dir, delete=False
        )
        time.sleep(self._delta_tile)

    def run(self):
        while not self._stop:
            self._process_sync()


class BlissSequenceRSyncWorker(RSyncWorker):
    """Thread to synchronize a bliss sequence"""

    def __init__(
        self,
        src_dir,
        dst_dir,
        src_proposal_file,
        dst_proposal_file,
        src_sample_file,
        dst_sample_file,
        delta_time,
    ):
        super(BlissSequenceRSyncWorker, self).__init__(
            src_dir=src_dir, dst_dir=dst_dir, delta_time=delta_time
        )
        self._bliss_master_file = src_proposal_file
        self._dst_bliss_master_file = dst_proposal_file
        self._bliss_sample_file = src_sample_file
        self._dst_bliss_sample_file = dst_sample_file

    def _process_sync(self):
        super(BlissSequenceRSyncWorker, self)._process_sync()
        if self._bliss_master_file is not None:
            RSyncManager().sync_file(
                source=self._bliss_master_file, target=self._dst_bliss_master_file
            )
        if self._bliss_sample_file is not None:
            RSyncManager().sync_file(
                source=self._bliss_sample_file, target=self._dst_bliss_sample_file
            )


class BlissSequenceRSyncWorkerFinalizer(qt.QThread):
    def __init__(
        self,
        source_scans,
        target_scans,
        proposal_file,
        target_proposal_file,
        sample_file,
        target_sample_file,
        nx_file,
        target_nx_file,
        block,
        callback,
        callback_parameters,
        parallel,
        delta_time=0.5,
    ):
        self._sources_scans = source_scans
        self._target_scans = target_scans
        self._proposal_file = proposal_file
        self._target_proposal_file = target_proposal_file
        self._sample_file = sample_file
        self._target_sample_file = target_sample_file
        self._nx_file = nx_file
        self._target_nx_file = target_nx_file
        self._block = block
        self._callback = callback
        self._callback_parameters = callback_parameters
        self._parparallel = parallel

        self._n_callback_scans = 0
        self._n_callback_proposal = 0
        self._n_callback_sample = 0
        self._delta_time = delta_time

    def scan_transfert_completed(self):
        return self._n_callback_scans == len(self._sources_scans)

    def proposal_file_completed(self):
        if self._proposal_file is None:
            return True
        else:
            return self._n_callback_proposal == 1

    def sample_file_completed(self):
        if self._sample_file is None:
            return True
        else:
            return self._n_callback_sample == 1

    def transfert_completed(self):
        return (
            self.proposal_file_completed()
            and self.sample_file_completed()
            and self.scan_transfert_completed()
        )

    def _callback_scans(self, *args, **kwargs):
        self._n_callback_scans = self._n_callback_scans + 1

    def _callaback_sample_file(self, *args, **kwargs):
        self._n_callback_sample = 1

    def _callback_proposal_file(self, *args, **kwargs):
        self._n_callback_proposal = 1

    def run(self):
        # no callback
        if self._sample_file is not None:
            RSyncManager().sync_file(
                source=self._sample_file, target=self._target_sample_file
            )

        if self._proposal_file is not None:
            RSyncManager().sync_file(
                source=self._proposal_file, target=self._target_proposal_file
            )

        for scan_in, scan_out in zip(self._sources_scans, self._target_scans):
            RSyncManager().sync_file(
                source=scan_in,
                target=scan_out,
                callback=self._callback_scans,
                delete=True,
            )

        while not self.transfert_completed():
            time.sleep(self._delta_time)

        if self._callback:
            if self._callback_parameters is not None:
                self._callback(*self._callback_parameters)
            else:
                self._callback()
