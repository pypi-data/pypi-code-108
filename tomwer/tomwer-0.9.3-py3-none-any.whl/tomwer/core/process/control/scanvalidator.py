# coding: utf-8
# ##########################################################################
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
# ###########################################################################

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "18/06/2017"

from collections import OrderedDict
from tomwer.core.signal import Signal
from tomwer.core import settings
from tomwer.core import utils
from tomwer.core.process.task import BaseProcessInfo
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.utils import logconfig
import logging
from tomwer.core.scan.scanbase import TomwerScanBase, _TomwerBaseDock
from ewokscore.task import Task as EwoksTask

logger = logging.getLogger(__name__)


class _ScanValidatorPlaceHolder(EwoksTask, input_names=["data"], output_names=["data"]):
    def run(self):
        self.outputs.data = self.inputs.data


class ScanValidator(BaseProcessInfo):
    """
    Simple workflow locker until the use validate scans

    :param int memReleaserWaitLoop: the time to wait in second between two
                                    memory overload if we are in lbsram.
    """

    def __init__(self, memoryReleaser):
        super().__init__()
        self._scansToValidate = OrderedDict()
        self._manualValidation = True
        self._hasToLimitScanBlock = settings.isOnLbsram()
        self._memoryReleaser = memoryReleaser
        self._scans = {}
        """associate scanId (keys) to :class:`.TomoBase` object (value)"""

        # add callback _loopMemoryReleaserto free memory if necessary on lbsram
        if self._hasToLimitScanBlock:
            self._memoryReleaser.finished.connect(self._loopMemoryReleaser)
            self._memoryReleaser.start()

    def __del__(self):
        self._clearMemoryReleaser()

    def _clearMemoryReleaser(self):
        if self._memoryReleaser is not None:
            self._memoryReleaser.should_be_stopped = True
            self._memoryReleaser.wait()
            self._memoryReleaser = None

    @property
    def lastReceivedRecons(self):
        return list(self._scansToValidate.values())[0]

    def addScan(self, scan):
        """
        Return the index on the current orderred dict

        :param scan:
        :return:
        """
        _ftserie = scan
        if type(scan) is str:
            _ftserie = ScanFactory.create_scan_object(_ftserie)
        info = "Scan %s has been added by the Scan validator" % _ftserie
        logger.info(info)

        _ftserie = scan
        if type(scan) is str:
            _ftserie = ScanFactory.create_scan_object(_ftserie)
        self._scansToValidate[str(_ftserie)] = _ftserie

        index = len(self._scansToValidate) - 1

        self._freeStackIfNeeded()
        return index

    def _freeStackIfNeeded(self):
        # if we are low in memory in lbsram: we will automatically validate the current scan
        isLowMemoryLbs = utils.isLowOnMemory(settings.get_lbsram_path()) is True
        if not self.isValidationManual():
            self._validateStack()
        elif isLowMemoryLbs:
            mess = "low memory, free ScanValidator stack "
            logger.processSkipped(mess)
            self._validateStack(filter_="lbsram")

    def _loopMemoryReleaser(self):
        """
        simple loop using the _memoryReleaser and calling the
        _freeStackIfNeeded function
        """
        self._freeStackIfNeeded()
        if self._memoryReleaser and not hasattr(
            self._memoryReleaser, "should_be_stopped"
        ):
            self._memoryReleaser.start()

    def _validateStack(self, filter_=None):
        """
        :param filter: can be None or 'lbsram' if lbsram will only free scan
                       located on lbsram.
        Validate all the scans in the stack.
        """
        for scanID in list(self._scansToValidate.keys()):
            scan = self._scansToValidate[scanID]
            if filter_ is None or settings.isOnLbsram(scan):
                self._validated(scan)

    def _validateScan(self, scan):
        """This will validate the ftserie currently displayed

        :warning: this will cancel the currently displayed reconstruction.
            But if we are validating a stack of ftserie make sure this is the
            correct one you want to validate.
            Execution order in this case is not insured.
        """
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            self._validated(scan)

    def _cancelScan(self, scan):
        """This will cancel the ftserie currently displayed

        :warning: this will cancel the currently displayed reconstruction.
            But if we are validating a stack of ftserie make sure this is the
            correct one you want to validate.
            Execution order in this case is not insured.
        """
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            self._canceled(scan)

    def _redoAcquisitionScan(self, scan):
        """This will emit a signal to request am acquisition for the current
        ftSerieReconstruction

        :warning: this will cancel the currently displayed reconstruction.
            But if we are validating a stack of ftserie make sure this is the
            correct one you want to validate.
            Execution order in this case is not insured.
        """
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            self._redoacquisition(scan)

    # ------ callbacks -------
    def _validated(self, scan):
        """Callback when the validate button is pushed"""
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            info = "%s has been validated" % str(scan)
            logger.processEnded(
                info,
                extra={
                    logconfig.DOC_TITLE: self._scheme_title,
                    logconfig.SCAN_ID: str(scan),
                },
            )
            self._sendScanReady(scan)
            # in some case the scan can not be in the _scansToValidate
            # (if the signal) come from an other window that 'scan to treat'
            if str(scan) in self._scansToValidate:
                del self._scansToValidate[str(scan)]
            if str(scan) in self._scans:
                del self._scans[str(scan)]

    def _canceled(self, scan):
        """Callback when the cancel button is pushed"""
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            info = "%s has been canceled" % str(scan)
            logger.processEnded(
                info,
                extra={
                    logconfig.DOC_TITLE: self._scheme_title,
                    logconfig.SCAN_ID: str(scan),
                },
            )
            self._sendScanCanceledAt(scan)
            # in some case the scan can not be in the _scansToValidate
            # (if the signal) come from an other window that 'scan to treat'
            if str(scan) in self._scansToValidate:
                del self._scansToValidate[str(scan)]
            if str(scan) in self._scansToValidate:
                del self._scans[str(scan)]
            self.clear()

    def _redoacquisition(self, ftserie):
        """Callback when the redo acquisition button is pushed"""
        raise NotImplementedError("_redoacquisition not implemented yet")

    def _changeReconsParam(self, ftserie):
        """Callback when the change reconstruction button is pushed"""
        if ftserie is None:
            return

        _ftserie = ftserie
        if type(ftserie) is str:
            _ftserie = ScanFactory.create_scan_object(_ftserie)

        if _ftserie.path in self._scansToValidate:
            del self._scansToValidate[str(_ftserie)]
        self._sendUpdateReconsParam(_TomwerBaseDock(tomo_instance=_ftserie))

    def setManualValidation(self, b):
        """if the validation mode is setted to manual then we will wait for
        user approval before validating. Otherwise each previous and next scan
        will be validated

        :param boolean b: False if we want an automatic validation
        """
        self._manualValidation = b
        if not self.isValidationManual():
            self._validateStack()

    def isValidationManual(self):
        """

        :return: True if the validation is waiting for user interaction,
                 otherwise False
        """
        return self._manualValidation

    def _sendScanReady(self):
        raise RuntimeError("ScanValidator is a pure virtual class.")

    def _sendScanCanceledAt(self):
        raise RuntimeError("ScanValidator is a pure virtual class.")

    def _sendUpdateReconsParam(self):
        raise RuntimeError("ScanValidator is a pure virtual class.")

    def clear(self):
        scans = self._scans.values()
        for scan in scans:
            self._cancelScan(scan=scans[scan])


class ScanValidatorP(ScanValidator):
    """
    For now to avoid multiple inheritance from QObject with the process widgets
    we have to define two classes. One only for the QObject inheritance.

    :param int memReleaserWaitLoop: the time to wait in second between two
                                    memory overload if we are in lbsram.
    """

    scanReady = Signal(TomwerScanBase)
    """Signal emitted when a scan is ready"""
    scanCanceledAt = Signal(str)
    """Signal emitted when a scan has been canceled"""
    updateReconsParam = Signal(TomwerScanBase)
    """Signal emitted when a scan need to be reconstructed back with new
    parameters"""

    def __init__(self, memoryReleaser=None):
        ScanValidator.__init__(self, memoryReleaser)

    def _sendScanReady(self, scan):
        self.scanReady.emit(scan)

    def _sendScanCanceledAt(self, scan):
        self.scanCanceledAt.emit(scan)

    def _sendUpdateReconsParam(self, scan):
        self.updateReconsParam.emit(scan)
