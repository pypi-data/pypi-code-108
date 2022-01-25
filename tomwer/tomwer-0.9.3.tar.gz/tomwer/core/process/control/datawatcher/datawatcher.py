# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
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

"""This module analyze headDir data directory
   to detect scan to be reconstructed
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "30/09/2019"

import os
import time
import threading
from tomwer.core.signal import Signal
from tomwer.core.process.utils import LastReceivedScansDict
from tomwer.core.process.task import BaseProcessInfo
from tomwer.core.process.control.datawatcher.datawatcherobserver import (
    _DataWatcherObserver,
    _OngoingObservation,
)
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.settings import get_lbsram_path, get_dest_path
from tomwer.core.utils import logconfig
from .status import *  # noqa F403
import logging
from tomwer.core.scan.scanbase import TomwerScanBase
from ewokscore.task import Task as EwoksTask

logger = logging.getLogger(__name__)


class _DataWatchertaskPlaceHolder(EwoksTask, output_names=("data",)):
    pass


class _DataWatcher(BaseProcessInfo):
    # TODO: change: this is not properly a Task
    """DataWatcher is the class use to mange observation of scans

    It basically have one DataWatcherObserver thread which is dealing with the
        observations. It parse all folder contained under the RootDir.

    This DataWatcherObserver is run every `maxWaitBtwObsLoop`. The call to the
    DataWatcherObserver is managed by the `loopObservationThread` which is calling
    back `_launchObservation`

    DataWatcher can run infinite search or stop observation after the discovery
    of the first valid scan (`setInfiniteIteration`)
    """

    folderObserved = None

    NB_STORED_LAST_FOUND = 20
    """All found acquisition are stored until we reach this number. In this
    case the oldest one will be removed"""

    DEFAULT_OBS_METH = DET_END_XML  # noqa F405

    def __init__(self):
        super().__init__()
        """use to know if we want to continue observation when the finished
        scan is found ?"""
        self.lastFoundScans = LastReceivedScansDict(self.NB_STORED_LAST_FOUND)
        self.isObserving = False
        self._initClass()

        # get ready observation
        self._setCurrentStatus("not processing")
        self._launchObservation()
        self._checkThread = None

    def _initClass(self):
        self.srcPattern = get_lbsram_path()
        self.destPattern = get_dest_path()

        self.observationThread = None
        """Thread used to parse directories and found where some
        :class`DataWatcherFixObserver` have to be launcher"""
        self.obsThIsConnected = False
        self.maxWaitBtwObsLoop = 5
        """time between two observation loop, in sec"""
        self.obsMethod = self.DEFAULT_OBS_METH
        """Pattern to look in the acquisition file to know of the acquisition
         is ended or not"""
        self.startByOldest = False

    def _switchObservation(self):
        """Switch the status of observation"""
        if self.isObserving is True:
            self.stop()
        else:
            self.start()

    def setObsMethod(self, obsMethod):
        """Set the observation method to follow.

        .. Note:: For now this will be apply on the next observation iteration.
                  We don't wan't to stop and restart an observation as sometimes
                  It can invoke a lot of start/stop if the user is editing the
                  pattern of the file for example. But this might evolve in the
                  future.
        """
        assert type(obsMethod) in (str, tuple)
        if type(obsMethod) is tuple:
            assert len(obsMethod) == 1 or (
                type(obsMethod[1]) is dict and len(obsMethod) == 2
            )
        self.obsMethod = obsMethod
        if self.isObserving:
            self._restartObservation()

    def setObservation(self, b):
        """Start a new observation (if none running ) or stop the current
        observation

        :param bool b: the value to set to the observation
        """
        self.start() if b else self.stop()

    def stop(self, sucess=False):
        """
        Stop the thread of observation

        :param bool sucess: if True this mean that we are stopping the
                            observation because we found an acquisition
                            finished. In this case we don't want to update the
                            status and the log message

        """
        if self.isObserving is False:
            return False

        self._setIsObserving(False)
        if self.observationThread is not None:
            # remove connection
            self.observationThread.quitEvent.set()
            if self.observationThread.is_alive():
                self.observationThread.join()
            if self._checkThread and self._checkThread.is_alive():
                self._checkThread.join()
            self.observationThread = None

        if sucess is False:
            self._setCurrentStatus(str("not processing"))
        logger.info("stop observation from %s" % self.folderObserved)

        return True

    def start(self):
        """Start the thread of observation

        :return bool: True if the observation was started. Otherwise this
           mean that an observation was already running
        """
        if self.isObserving is True:
            return False
        else:
            logger.info("start observation from %s" % self.folderObserved)
            self._setIsObserving(True)
            self._setCurrentStatus("not processing")
            self._launchObservation()

            return True

    def isObserving(self):
        """

        :return bool: True if the widget is actually observing the root
                      directory

        """
        return self.isObserving

    def _setIsObserving(self, b):
        self.isObserving = b

    def resetStatus(self):
        """
        Reset the status to not processing. Needed to restart observation,
        like when the folder is changing
        """
        self._setCurrentStatus("not processing")

    def getFolderObserved(self):
        return self.folderObserved

    def setFolderObserved(self, path):
        assert type(path) is str
        if not os.path.isdir(path):
            warning = "Can't set the observe folder to ", path, " invalid path"
            logger.warning(warning, extra={logconfig.DOC_TITLE: self._scheme_title})
        else:
            self.folderObserved = os.path.abspath(path)

    def getTimeBreakBetweenObservation(self):
        """

        :return: the duration of the break we want to do between two
            observations (in sec)
        """
        return self.maxWaitBtwObsLoop

    def setWaitTimeBtwLoop(self, time):
        if not time > 0:
            err = "invalid time given %s" % time
            raise ValueError(err)
        self.maxWaitBtwObsLoop = time

    def setStartByOldest(self, b):
        """
        When parsing folders, should we start by the oldest or the newest file

        :param bool b: if True, will parse folders from the oldest one
        """
        self.startByOldest = b

    def setSrcAndDestPattern(self, srcPattern, destPattern):
        """Set the values of source pattern and dest pattern

        :param str or None srcPattern: the value to set to the source pattern
                                       (see datawatcher)
        :param str or None destPattern: the value to set to the destination
                                        pattern (see datawatcher)
        """
        self.srcPattern = srcPattern
        self.destPattern = destPattern

    def _initObservation(self):
        """Init the thread running the datawatcher functions"""
        if self.observationThread is None:
            self._createDataWatcher()

        headDir = self.getFolderObserved()
        if headDir is None or not os.path.isdir(headDir):
            self._messageNotDir(headDir)
            self.stop()
            return False

        # update information on the head folder and the start by the oldest
        self.observationThread.setHeadFolder(headDir)
        self.observationThread.setObservationMethod(self.obsMethod)

        return True

    def _messageNotDir(self, dir):
        message = "Given path (%s) isn't a directory." % dir
        logger.warning(message, extra={logconfig.DOC_TITLE: self._scheme_title})

    def _createDataWatcher(self):
        self.observationThread = _DataWatcherObserver(
            observationClass=self._getObservationClass(),
            obsMethod=self.obsMethod,
            time_between_loops=self.maxWaitBtwObsLoop,
            srcPattern=self.srcPattern,
            destPattern=self.destPattern,
        )

    def _observation_thread_running(self):
        return self.observationThread is not None and self.observationThread.is_alive()

    def _init_check_finished_scan(self):
        self._checkThread = threading.Thread(target=self._check_finished_scan)
        self._checkThread.start()

    def _getObservationClass(self):
        return _OngoingObservation

    def _check_finished_scan(self):
        """check scanReady event"""
        while self.isObserving is True:
            if self.observationThread is not None:
                self.observationThread._check_scans_ready()
                with self.observationThread.lock:
                    if self.observationThread.scanReadyEvent.isSet():
                        for scanID in self.observationThread.latestScanReady:
                            try:
                                _scan = ScanFactory.create_scan_object(scan_path=scanID)
                            except Exception as e:
                                logger.error(
                                    "Fail to create TomoBase from",
                                    scanID,
                                    "Error is",
                                    e,
                                )
                            else:
                                self._signalScanReady(scan=_scan)
                        self.observationThread.scanReadyEvent.clear()
            time.sleep(0.05)

    def _restartObservation(self):
        """Reset system to launch a new observation"""
        if self.observationThread is not None:
            self.observationThread.quit()
            self._setCurrentStatus("not processing")
            self._launchObservation()

    def _statusChanged(self, status):
        assert status[0] in OBSERVATION_STATUS  # noqa 320
        self._setCurrentStatus(status[0], status[1] if len(status) == 2 else None)

    def informationReceived(self, info):
        logger.info(info)

    def _setCurrentStatus(self, status, info=None):
        """Change the current status to status"""
        assert type(status) is str
        assert status in OBSERVATION_STATUS  # noqa 320
        self.currentStatus = status
        self._updateStatusView()
        if hasattr(self, "sigTMStatusChanged"):
            self.sigTMStatusChanged.emit(status)

        _info = status
        if info is not None:
            _info += " - " + info

        self.informationReceived(_info)

        if status == "acquisition ended":
            # info should be the directory path
            assert info is not None
            assert type(info) is str
            logger.processEnded(
                "Find a valid scan",
                extra={
                    logconfig.DOC_TITLE: self._scheme_title,
                    logconfig.SCAN_ID: info,
                },
            )
            try:
                scan = ScanFactory.create_scan_object(scan_path=info)
            except Exception as e:
                logger.warning("Fail to create scan object from", info, "Reason is", e)
            else:
                self._signalScanReady(scan=scan)

    def _signalScanReady(self, scan):
        assert isinstance(scan, TomwerScanBase)
        self.lastFoundScans.add(scan)
        self.sigScanReady.emit(scan)

    def mockObservation(self, folder):
        # simple mocking emitting a signal to say that the given folder is valid
        self._setCurrentStatus(status="acquisition ended", info=folder)

    def _updateStatusView(self):
        pass

    def _setMaxAdvancement(self, max):
        """ """
        pass

    def _advance(self, nb):
        """Update the progress bar"""
        pass

    def set_configuration(self, properties):
        for observe_folder_alias in ("observed_folder", "folderObserved"):
            if observe_folder_alias in properties:
                self.setFolderObserved(properties[observe_folder_alias])

    def waitForObservationFinished(self):
        if self.observationThread is not None:
            self.observationThread.waitForObservationFinished()
            self.observationThread.quitEvent.set()

    def getIgnoredFolders(self):
        if self.observationThread is None:
            return []
        else:
            return self.observationThread.observations.ignoredFolders


class DataWatcher(_DataWatcher):
    """For now to avoid multiple inheritance from QObject with the process
    widgets
    we have to define two classes. One only for the QObject inheritance
    """

    sigTMStatusChanged = Signal(str)
    sigScanReady = Signal(TomwerScanBase)

    import threading

    scan_found_event = threading.Event()

    def __init__(self):
        _DataWatcher.__init__(self)
        self.scan = None
        """last found scan"""

    def _signalScanReady(self, scan):
        assert isinstance(scan, TomwerScanBase)
        super()._signalScanReady(scan)
        if self._return_dict:
            value = scan.to_dict()
        else:
            value = scan
        self.register_output(key="data", value=value)
        self.scan_found_event.set()

    def _launchObservation(self):
        """Main function of the widget"""
        if self.isObserving is False:
            return

        # manage data watcher observation
        if self.observationThread is None or not self._observation_thread_running():
            if self._initObservation() is False:
                self.currentStatus = self._setCurrentStatus("failure")
                logger.info(
                    "failed on observation",
                    extra={logconfig.DOC_TITLE: self._scheme_title},
                )
                return

        self._init_check_finished_scan()

        # starting the observation thread
        self.observationThread.start()
