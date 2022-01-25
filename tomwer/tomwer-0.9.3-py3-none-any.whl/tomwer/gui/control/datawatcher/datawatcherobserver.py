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
__date__ = "10/01/2019"


import os
from silx.gui import qt
from tomwer.core.process.control.datawatcher.datawatcherobserver import (
    _OngoingObservation,
)
from tomwer.core.process.control.datawatcher.datawatcherobserver import (
    _DataWatcherObserver_MixIn,
)
from tomwer.core.process.control.datawatcher.datawatcherobserver import (
    _DataWatcherFixObserverMixIn,
)
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.process.control.datawatcher import status as datawatcherstatus
import logging
from tomwer.core.scan.scanfactory import ScanFactory

logger = logging.getLogger(__name__)


class _QDataWatcherObserver(_DataWatcherObserver_MixIn, qt.QThread):
    """
    DatWatcherObserver implementation with a qt.QThread

    We have two implementations in order to avoid hard dependancy on qt for
    tomwer.core package
    """

    sigScanReady = qt.Signal(TomwerScanBase)

    def __init__(
        self,
        obsMethod,
        observationClass,
        headDir=None,
        startByOldest=False,
        srcPattern=None,
        destPattern=None,
        ignoredFolders=None,
    ):
        qt.QThread.__init__(self)
        _DataWatcherObserver_MixIn.__init__(
            self,
            obsMethod=obsMethod,
            observationClass=observationClass,
            headDir=headDir,
            startByOldest=startByOldest,
            srcPattern=srcPattern,
            destPattern=destPattern,
            ignoredFolders=ignoredFolders,
            time_between_loops=0.2,
        )
        self.observations.sigScanReady.connect(self._signalScanReady)

    def _signalScanReady(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.sigScanReady.emit(scan)

    def _getObserver(self, scanID):
        return _QDataWatcherFixObserver(
            scanID=scanID,
            obsMethod=self.obsMethod,
            srcPattern=self.srcPattern,
            destPattern=self.destPattern,
            patternObs=self._patternObs,
            observationRegistry=self.observations,
        )

    def run(self):
        def process(directory):
            if (
                self.observations.isObserving(directory) is False
                and self.dataWatcherProcess._isScanDirectory(directory)
                and directory not in self.observations.ignoredFolders
            ):
                self.observe(directory)

            try:
                for f in os.listdir(directory):
                    if os.path.isdir(os.path.join(directory, f)):
                        process(os.path.join(directory, f))
            except Exception:
                pass

        if not os.path.isdir(self.headDir):
            logger.warning("can't observe %s, not a directory" % self.headDir)
            return
        self.dataWatcherProcess = self._getDataWatcherProcess()
        process(self.headDir)

        self._processObservation()

    def waitForObservationFinished(self, timeOut=10):
        threads = list(self.observations.dict.values())
        for thread in threads:
            thread.wait(timeOut)

    def wait(self, *args, **kwargs):
        self.waitForObservationFinished()
        super(_QDataWatcherObserver, self).wait(*args, **kwargs)


class _QOngoingObservation(_OngoingObservation, qt.QObject):
    """
    _OngoingObservation with a QObject and signals for each event
    """

    sigScanReady = qt.Signal(TomwerScanBase)
    """Emitted when a finished acquisition is detected"""
    sigObsAdded = qt.Signal(str)
    """Signal emitted when an observation is added"""
    sigObsRemoved = qt.Signal(str)
    """Signal emitted when an observation is removed"""
    sigObsStatusReceived = qt.Signal(str, str)
    """Signal emitted when receiving a new observation status"""

    def __init__(self):
        qt.QObject.__init__(self)
        _OngoingObservation.__init__(self)

    def _acquisition_ended(self, scanID):
        _OngoingObservation._acquisition_ended(self, scanID=scanID)
        try:
            scan = ScanFactory.create_scan_object(scan_path=scanID)
        except Exception as e:
            logger.error("Fail to create TomoBase instance from", scanID, "Error is", e)
        else:
            self.sigScanReady.emit(scan)

    def add(self, observer):
        already_observing = self.isObserving(observer.path)
        _OngoingObservation.add(self, observer=observer)
        if not already_observing:
            observer.sigStatusChanged.connect(self._updateStatus)
            self.sigObsAdded.emit(observer.path)

    def remove(self, observer):
        observing = self.isObserving(observer.path)
        _OngoingObservation.remove(self, observer=observer)
        if observing is True:
            observer.sigStatusChanged.disconnect(self._updateStatus)
            self.sigObsRemoved.emit(observer.path)

    def _updateStatus(self, status, scan):
        if self.isObserving(scan) is True:
            self.sigObsStatusReceived.emit(
                scan, datawatcherstatus.DICT_OBS_STATUS[status]
            )
        _OngoingObservation._updateStatus(self, status=status, scan=scan)

    def reset(self):
        # self.ignoreFolders = []
        for scanID, observer in self.dict:
            observer.sigStatusChanged.disconnect(self._updateStatus)
            observer.quit()
        self.dict = {}


class _QDataWatcherFixObserver(_DataWatcherFixObserverMixIn, qt.QThread):
    """
    Implementation of the _DataWatcherFixObserverMixIn with a qt.QThread
    """

    sigStatusChanged = qt.Signal(int, str)
    """signal emitted when the status for a specific directory change
    """

    def __init__(
        self,
        scanID,
        obsMethod,
        srcPattern,
        destPattern,
        patternObs,
        observationRegistry,
    ):
        qt.QThread.__init__(self)
        _DataWatcherFixObserverMixIn.__init__(
            self,
            scanID=scanID,
            obsMethod=obsMethod,
            srcPattern=srcPattern,
            destPattern=destPattern,
            patternObs=patternObs,
            observationRegistry=observationRegistry,
        )

    def run(self):
        if not os.path.isdir(self.path):
            logger.info("can't observe %s, not a directory" % self.path)
            self.status = "failure"
            self.sigStatusChanged.emit(
                datawatcherstatus.OBSERVATION_STATUS[self.status], self.path
            )
            self.validation = -1
            return

        try:
            scan = ScanFactory.create_scan_object(scan_path=self.path)
        except ValueError as e:
            logger.error(e)
        else:
            if scan.is_abort(
                src_pattern=self.srcPattern, dest_pattern=self.destPattern
            ):
                if self.status != "aborted":
                    logger.info("Acquisition %s has been aborted" % self.path)
                    self.dataWatcherProcess._removeAcquisition(
                        scanID=self.path, reason="acquisition aborted by the user"
                    )

                    self.status = "aborted"
                self.sigStatusChanged.emit(
                    datawatcherstatus.OBSERVATION_STATUS[self.status], self.path
                )
                self.validation = -2
                return
            dataComplete = self.dataWatcherProcess.is_data_complete()

            if dataComplete is True:
                self.status = "acquisition ended"
                self.sigStatusChanged.emit(
                    datawatcherstatus.OBSERVATION_STATUS[self.status], self.path
                )
                self.validation = 1
            else:
                self.status = "waiting for acquisition ending"
                self.sigStatusChanged.emit(
                    datawatcherstatus.OBSERVATION_STATUS[self.status], self.path
                )
                self.validation = 0
        return
