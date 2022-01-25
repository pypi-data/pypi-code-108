# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
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

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "08/06/2017"


import os
from queue import Queue
from silx.gui import qt
from tomwer.core import settings
from tomwer.core import utils
from tomwer.core.utils.scanutils import MockEDF
from tomwer.core.process.reconstruction.ftseries.params import fastsetupdefineglobals
from tomwer.core.process.reconstruction.ftseries import (
    run_reconstruction_from_recons_params,
)
from tomwer.core.utils import logconfig
from tomwer.core.utils.Singleton import singleton
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.web.client import OWClient
from processview.core.superviseprocess import SuperviseProcess
from processview.core.manager import ProcessManager, DatasetState
import logging

logger = logging.getLogger(__name__)


@singleton
class ReconstructionStack(qt.QObject, Queue, OWClient, SuperviseProcess):
    """
    Manage a stack of ftseries reconstruction
    """

    sigReconsFinished = qt.Signal(TomwerScanBase)
    sigReconsFailed = qt.Signal(TomwerScanBase)
    sigReconsMissParams = qt.Signal(TomwerScanBase)
    sigReconsStarted = qt.Signal(TomwerScanBase)

    def __init__(self, process_id=None):
        qt.QObject.__init__(self)
        Queue.__init__(self)
        OWClient.__init__(self)
        SuperviseProcess.__init__(self, process_id=process_id)
        self.reconsThread = _ReconsFtSeriesThread(process_id=process_id)
        self.reconsThread.sigThReconsFinished.connect(self._dealWithFinishedRecons)
        self.reconsThread.sigThReconsFailed.connect(self._dealWithFailedRecons)
        self.reconsThread.sigThMissingParams.connect(self._dealWithThMissingParams)
        self._forceSync = False

    def add(self, scan, inputs):
        """
        add a reconstruction and will run it as soon as possible

        :param list slices: the list of slices to reconstruct
        :param scan: the folder of the acquisition to reconstruct
        :type scan: :class:`.TomoBase`
        :param dict inputs: parameters of the reconstruction
        """
        ProcessManager().notify_dataset_state(
            dataset=scan,
            process=self,
            state=DatasetState.PENDING,
        )
        if not isinstance(scan, TomwerScanBase):
            raise TypeError(f"{scan} is expected to be an instance of {TomwerScanBase}")
        # TODO: reconsparam could be taken dircetly from scan
        Queue.put(self, (scan, inputs))
        if self.canExecNext():
            self.execNext()

    def execNext(self):
        """Launch the next reconstruction if any"""
        if Queue.empty(self):
            return

        assert not self.reconsThread.isRunning()
        # TODO: reconsparam could be taken dircetly from scan
        scan, inputs = Queue.get(self)
        self.sigReconsStarted.emit(scan)
        self.reconsThread.init(scan, inputs)
        self.reconsThread.start()
        if self._forceSync is True:
            self.reconsThread.wait()

    def canExecNext(self):
        """
        Can we launch an ftserie reconstruction.
        Reconstruction can't be runned in parallel

        :return: True if no reconstruction is actually running
        """
        return not self.reconsThread.isRunning()

    def _dealWithFinishedRecons(self, scan):
        assert isinstance(scan, TomwerScanBase)
        info = "reconstruction %s is finished" % scan.path
        logger.info(info)
        self.sigReconsFinished.emit(scan)
        self.execNext()

    def _dealWithThMissingParams(self, scan):
        self.sigReconsMissParams.emit(scan)
        self.execNext()

    def _dealWithFailedRecons(self, scan):
        self.sigReconsFailed.emit(scan)
        self.execNext()

    def setMockMode(self, b):
        self.reconsThread.setMockMode(b)
        self.execNext()

    def setForceSync(self, b=True):
        self._forceSync = b

    def stop(self):
        """stop the stack and get back the thread"""
        self.queue.clear()
        self.blockSignals(True)
        self.reconsThread.blockSignals(True)
        self.reconsThread.wait()


class _ReconsFtSeriesThread(OWClient, qt.QThread, SuperviseProcess):
    """
    Simple thread launching ftseries reconstructions
    """

    copyH5FileReconsIntoFolder = False
    """if True then copy the file used for reconstruction into the scan
    folder under the copyH5ReconsName"""

    copyH5ReconsName = "octave_FT_params.h5"
    """Name under wich the reconstruction parameters will be saved if
    'copyH5FileReconsIntoFolder' is active"""

    sigThReconsFinished = qt.Signal(TomwerScanBase)
    "Emitted if reconstruction ended with success"
    sigThReconsFailed = qt.Signal(TomwerScanBase)
    "Emitted if reconstruction failed"
    sigThMissingParams = qt.Signal(TomwerScanBase)
    "Emitted if missing some reconstruction parameters"

    _mockMode = False

    def __init__(self, process_id=None):
        OWClient.__init__(self)
        # handle Qt different constructor requests
        try:
            qt.QThread.__init__(self, process_id=process_id)
        except TypeError:
            qt.QThread.__init__(self)
        SuperviseProcess.__init__(self, process_id=process_id)
        self.scan = None
        self.inputs = None

    def run(self):
        if self.scan is None or self.inputs is None:
            mess = "reconstruction not initialized. Can' reconstruct"
            logger.warning(mess)
            ProcessManager().notify_dataset_state(
                dataset=self.scan, process=self, state=DatasetState.FAILED, details=mess
            )

            self.sigThReconsFailed.emit(mess)
            return

        if not os.path.isdir(self.scan.path):
            mess = "%s is not a valid fodler, can't reconstruct"
            ProcessManager().notify_dataset_state(
                dataset=self.scan, process=self, state=DatasetState.FAILED, details=mess
            )
            self.sigThReconsFailed.emit(mess)
            return

        self._processRecons()

    def init(self, scan, inputs):
        assert isinstance(scan, TomwerScanBase)
        self.scan = scan
        self.inputs = inputs

    def _processRecons(self):
        if not isinstance(self.inputs, dict):
            raise TypeError(f"{self.inputs} is expected to be a dict")
        ProcessManager().notify_dataset_state(
            dataset=self.scan,
            process=self,
            state=DatasetState.ON_GOING,
        )
        self._noticeStart()
        # check is on low memory in lbsram
        if (
            settings.isOnLbsram(self.scan)
            and utils.isLowOnMemory(settings.get_lbsram_path()) is True
        ):
            # if computer is running into low memory in lbsram skip reconstruction
            mess = "low memory, skip reconstruction for " + self.scan.path
            logger.processSkipped(mess)
            ProcessManager().notify_dataset_state(
                dataset=self.scan,
                process=self,
                state=DatasetState.SKIPPED,
                details=mess,
            )

            self.sigThReconsFinished.emit(self.scan)
        else:
            try:
                # deal with mock reconstruction
                if self._mockMode is True:
                    MockEDF.mockReconstruction(self.scan.path)
                else:
                    if not ("pyhst2_params" in self.inputs):
                        raise KeyError("'pyhst2_params' key is expected")
                    if not isinstance(self.inputs["pyhst2_params"], dict):
                        raise TypeError(
                            "value associated to pyhst2_params is expected to be a dict"
                        )
                    run_reconstruction_from_recons_params(
                        scan=self.scan, inputs=self.inputs
                    )
            except fastsetupdefineglobals.H5MissingParameters:
                ProcessManager().notify_dataset_state(
                    dataset=self.scan,
                    process=self,
                    state=DatasetState.FAILED,
                )
                self.sigThMissingParams.send(self, self.scan)
            else:
                ProcessManager().notify_dataset_state(
                    dataset=self.scan,
                    process=self,
                    state=DatasetState.SUCCEED,
                )

        self.sigThReconsFinished.emit(self.scan)

    def _noticeStart(self):
        info = "start reconstruction of %s" % self.scan.path
        logger.info(info, extra={logconfig.SCAN_ID: self.scan.path})

    def setMockMode(self, b):
        """If the mock mode is activated then during reconstruction won't call
        Octave script for reconstruction but will generate some output files
        according to convention

        :param boolean b: True if we want to active the mock mode
        """
        self._mockMode = b
