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
__date__ = "01/10/2018"


from queue import Queue
from silx.gui import qt
import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from processview.core.superviseprocess import SuperviseProcess
import copy
from tomwer.core.process.reconstruction.lamino.tofu import LaminoReconstruction
from tomwer.core.utils.Singleton import singleton
from tomwer.web.client import OWClient

logger = logging.getLogger(__name__)


@singleton
class LaminoReconstructionStack(qt.QObject, Queue, OWClient):
    """
    Manage a stack of lamino (tofu) reconstruction
    """

    sigReconsFinished = qt.Signal(TomwerScanBase)
    """Signal emitted when a new reconstruction is ended"""
    sigReconsFailed = qt.Signal(TomwerScanBase)
    """Signal emitted when a new reconstruction has failed"""
    sigReconsMissParams = qt.Signal(TomwerScanBase)
    """Signal emitted when some paramters are missing for the reconstruction"""
    sigReconsStarted = qt.Signal(TomwerScanBase)
    """Signal emitted when a new reconstruction is started"""

    def __init__(self, process_id=None):
        qt.QObject.__init__(self)
        Queue.__init__(self)
        OWClient.__init__(self)
        self.process_id = process_id
        self.reconsThread = _LaminoReconsThread(process_id=process_id)
        self.reconsThread.sigThReconsFinished.connect(self._dealWithFinishedRecons)
        self.reconsThread.sigThReconsFailed.connect(self._dealWithFailedRecons)
        self.reconsThread.sigThMissingParams.connect(self._dealWithThMissingParams)
        self._forceSync = False

    def add(
        self,
        recons_obj,
        recons_params,
        additional_opts,
        scan_id,
        remove_existing,
        callback,
    ):
        """
        add a reconstruction and will run it as soon as possible

        :param recons_obj: reconstructor, keeping trace of preprocess flat field
                           correction for example.
        :type recons_obj: LaminoReconstruction
        :param dict reconsParams: parameters of the reconstruction
        :param dict additional_opts: not managed directly by the gui
        :param scan_id: the folder of the acquisition to reconstruct
        :type: TomoBase
        :param bool remove_existing: if True then remove output dir before
                                     reconstruction
        :param callback: function to call after the reconstruction execution
        """
        assert isinstance(recons_obj, LaminoReconstruction)
        Queue.put(
            self,
            (
                recons_obj,
                recons_params,
                additional_opts,
                scan_id,
                remove_existing,
                callback,
            ),
        )
        if self.canExecNext():
            self.execNext()

    def execNext(self):
        """
        Launch the next reconstruction if any
        """
        if Queue.empty(self):
            return

        assert not self.reconsThread.isRunning()
        (
            recons_obj,
            recons_params,
            additional_opts,
            scan,
            remove_existing,
            callback,
        ) = Queue.get(self)
        self.sigReconsStarted.emit(scan)
        info = "start lamino reconstuction of {}".format(str(scan))
        logger.processStarted(info)
        self.reconsThread.init(
            recons_obj=recons_obj,
            recons_params=recons_params,
            additional_opts=additional_opts,
            scan_id=scan,
            remove_existing=remove_existing,
        )
        self.reconsThread.sigThReconsFinished.connect(callback)
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
        info = "lamino reconstruction of {} finished".format(str(scan))
        logger.processSucceed(info)
        self.sigReconsFinished.emit(scan)
        self.execNext()

    def _dealWithThMissingParams(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.sigReconsMissParams.emit(scan)
        self.execNext()

    def _dealWithFailedRecons(self, scan):
        assert isinstance(scan, TomwerScanBase)
        info = "reconstruction of {} failed".format(str(scan))
        logger.processFailed(info)
        self.sigReconsFailed.emit(scan)
        self.execNext()

    def setMockMode(self, b):
        self.reconsThread.setMockMode(b)
        self.execNext()

    def setForceSync(self, b=True):
        self._forceSync = b


class _LaminoReconsThread(qt.QThread, SuperviseProcess):
    """Thread used for running lamino reconstrucion using Tofu"""

    sigThReconsFinished = qt.Signal(TomwerScanBase)
    "Emitted if reconstruction ended with success"
    sigThReconsFailed = qt.Signal(TomwerScanBase)
    "Emitted if reconstruction failed"
    sigThMissingParams = qt.Signal(TomwerScanBase)
    "Emitted if missing some reconstruction parameters"

    def __init__(self, process_id):
        try:
            qt.QThread.__init__(self, process_id=process_id)
        except TypeError:
            qt.QThread.__init__(self)
        SuperviseProcess.__init__(self, process_id=process_id)
        self.scan = None
        self.recons_params = None
        self.additional_opts = None
        self.callback = None
        self.remove_existing = False

    def init(
        self, recons_obj, recons_params, additional_opts, remove_existing, scan_id
    ):
        assert isinstance(recons_obj, LaminoReconstruction)
        self.recons_obj = recons_obj
        self.recons_params = recons_params
        self.additional_opts = additional_opts
        self.remove_existing = remove_existing
        self.scan = scan_id

    def run(self):
        # we need to create an other LaminoReconstruction object. Because
        # recons parameters might have changed bu we want to be up to date
        # regarding the flat field preprocessed already if any to avoid
        # several computation
        recons_obj = copy.deepcopy(self.recons_obj)
        recons_obj.reconstruction_parameters = self.recons_params
        recons_obj.additional_reco_options = self.additional_opts
        try:
            recons_obj.process(scan=self.scan)
        except ValueError as error:
            logger.warning(error)
            self.sigThMissingParams.emit(
                "Some parameters are missing or are incoherent"
            )
        except Exception as error:
            logger.error(
                "fail to run lamino reconstruction for %s reason is "
                "%s" % (self.scan, error)
            )
            self.sigThReconsFailed.emit(
                "fail to run reconstruction %s" % self.scan.path
            )
        else:
            self.sigThReconsFinished.emit(self.scan)
