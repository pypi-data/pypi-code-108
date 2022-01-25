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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "18/02/2018"


import os
import logging
from silx.gui import qt, icons as silxicons
from tomwer.io.utils import get_default_directory
from tomwer.core.process.control.datawatcher.datawatcher import _DataWatcher
from tomwer.gui.utils.waiterthread import QWaiterThread
from tomwer.gui.control import observations, history, datareacheractions
from tomwer.gui.control.datawatcher import configuration
from .datawatcherobserver import _QOngoingObservation
from .datawatcherobserver import _QDataWatcherObserver
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.utils import logconfig
from tomwer.core.scan.scanbase import TomwerScanBase

logger = logging.getLogger(__name__)


class DataWatcherWidget(_DataWatcher, qt.QMainWindow):
    """
    Widget used to display the on-going acquisitions and the finished one.

    :param parent: the parent widget
    """

    _textStopObservation = "Stop observation"
    _textStartObservation = "Start observation"

    obsStatusToWidgetStatus = {
        "not processing": "Not processed",
        "none found": "Running",
        "starting": "Running",
        "started": "Running",
        "waiting for acquisition ending": "Running",
        "acquisition ended": "Executed",
        "acquisition canceled": "Failed",
        "failure": "Failed",
    }

    _animatedStates = (
        "none found",
        "parsing",
        "waiting for acquisition ending",
        "starting",
        "started",
    )

    DEFAULT_DIRECTORY = "/lbsram/data/visitor"

    # TODO: status should also pass a TomoBase instance
    sigTMStatusChanged = qt.Signal(str)
    """Signal emitted when the changed"""
    sigScanReady = qt.Signal(TomwerScanBase)
    """Signal emitted when a scan is considered as ready"""
    sigFolderObservedChanged = qt.Signal()
    """Signal emitted when the user change the observed folder"""
    sigObservationStart = qt.Signal()
    """Signal emitted when the observation starts"""
    sigObservationEnd = qt.Signal()
    """Signal emitted when the observation end"""

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self._maxAdv = 100  # maximal progress bar advancement
        self._configWindow = None
        """Widget containing the configuration of the watcher"""
        self._historyWindow = None
        """Widget containing the latest valid scan found by the watcher"""
        self._observationWidget = None
        """Widget containing the current observed directory by the watcher"""
        self.controlWidget = None
        """Widget containing the 'control' of the datawatcher: select folder,
        status ..."""
        _DataWatcher.__init__(self)
        self.setFolderObserved(self.folderObserved)

    def _initClass(self):
        self.loopObservationThread = None
        _DataWatcher._initClass(self)
        toolbar = qt.QToolBar("", parent=self)
        toolbar.setIconSize(qt.QSize(32, 32))
        self._controlAction = datareacheractions.ControlAction(parent=self)
        self._observationsAction = datareacheractions.ObservationAction(parent=self)
        self._configurationAction = datareacheractions.ConfigurationAction(parent=self)
        self._historyAction = datareacheractions.HistoryAction(parent=self)
        toolbar.addAction(self._controlAction)
        toolbar.addAction(self._observationsAction)
        toolbar.addAction(self._configurationAction)
        toolbar.addAction(self._historyAction)

        self._actionGroup = qt.QActionGroup(self)
        self._actionGroup.addAction(self._controlAction)
        self._actionGroup.addAction(self._observationsAction)
        self._actionGroup.addAction(self._configurationAction)
        self._actionGroup.addAction(self._historyAction)

        self.addToolBar(qt.Qt.LeftToolBarArea, toolbar)
        toolbar.setMovable(False)

        self._buildGUI()

        # set initial path to observe
        self.setFolderObserved(self._getInitPath())
        self._initStatusView()

        # hide all windows by default
        for widget in (
            self.getControlWindow(),
            self.getObservationWidget(),
            self.getConfigWindow(),
            self.getHistoryWindow(),
        ):
            widget.setVisible(False)

        # deal with toolbar connection
        self._controlAction.toggled[bool].connect(self.getControlWindow().setVisible)
        self._observationsAction.toggled[bool].connect(
            self.getObservationWidget().setVisible
        )
        self._configurationAction.toggled[bool].connect(
            self.getConfigWindow().setVisible
        )
        self._historyAction.toggled[bool].connect(self.getHistoryWindow().setVisible)

        self._controlAction.setChecked(True)

    def close(self):
        logger.info("closing the datawatacher")
        self.stop()
        if self.loopObservationThread is not None:
            self.loopObservationThread.blockSignals(True)
            self._disconnectObserverThread()
            self.loopObservationThread.wait()
            self.loopObservationThread = None
        if self.observationThread.isRunning():
            self.observationThread.blockSignals(True)
            self.observationThread.wait()
            self.observationThread = None
        super(DataWatcherWidget, self).close()

    def getConfigWindow(self):
        if self._configWindow is None:
            self._configWindow = configuration._DWConfigurationWidget(parent=self)
            self._configWindow.startByOldestStateChanged.connect(self.setStartByOldest)
            self._configWindow.startByOldestStateChanged.connect(
                self._restartObservation
            )
        return self._configWindow

    def getObservationWidget(self):
        if self._observationWidget is None:
            self._observationWidget = observations.ScanObservation(parent=self)
            if self.observationThread:
                self._observationWidget.setOnGoingObservations(
                    self.observationThread.observations
                )
        return self._observationWidget

    def _changeCentralWidget(self, widget, action):
        actions = (
            self._historyAction,
            self._observationsAction,
            self._configurationAction,
            self._controlAction,
        )
        for _action in actions:
            _action.blockSignals(True)

        for _action in actions:
            if _action != action:
                _action.setChecked(False)

        _widgets = (
            self.getControlWindow(),
            self.getObservationWidget(),
            self.getHistoryWindow(),
            self.getConfigWindow(),
        )
        for _widget in _widgets:
            _widget.setVisible(False)

        widget.setVisible(action.isChecked())
        for _action in actions:
            _action.blockSignals(False)

    def getControlWindow(self):
        if self.controlWidget is None:
            self.controlWidget = qt.QWidget(parent=self)
            self.controlWidget.setLayout(qt.QVBoxLayout())
            layout = self.controlWidget.layout()

            self.statusBar = qt.QStatusBar(parent=self.controlWidget)
            self._qlInfo = qt.QLabel(parent=self.controlWidget)

            layout.addWidget(self._getFolderSelection())
            layout.addWidget(self._qlInfo)
            layout.addWidget(self._buildStartStopButton())
            layout.addWidget(self.statusBar)

            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
            layout.addWidget(spacer)

        return self.controlWidget

    def _buildGUI(self):
        """Build the GUI of the widget"""
        self._mainWidget = qt.QWidget(parent=self)
        self._mainWidget.setLayout(qt.QVBoxLayout())
        self._mainWidget.layout().addWidget(self.getControlWindow())
        self._mainWidget.layout().addWidget(self.getConfigWindow())
        self._mainWidget.layout().addWidget(self.getObservationWidget())
        self._mainWidget.layout().addWidget(self.getHistoryWindow())
        self.setCentralWidget(self._mainWidget)

    def _buildStartStopButton(self):
        """
        Build the start/stop button in a QHLayout with one spacer on the left
        and one on the right
        """
        widget = qt.QWidget(self.controlWidget)
        layout = qt.QHBoxLayout()
        widget.setLayout(layout)

        # left spacer
        spacerL = qt.QWidget(widget)
        spacerL.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        layout.addWidget(spacerL)

        # button
        self._qpbstartstop = qt.QPushButton(self._textStartObservation)
        self._qpbstartstop.setAutoDefault(True)
        self._qpbstartstop.pressed.connect(self._switchObservation)
        layout.addWidget(self._qpbstartstop)

        # right spacer
        spacerR = qt.QWidget(widget)
        spacerR.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        layout.addWidget(spacerR)

        return widget

    def _buildLoopTimeBreak(self):
        """
        Build the spin box to define the break we want to make between two
        observations
        """
        widget = qt.QWidget(self.controlWidget)
        layout = qt.QHBoxLayout()
        widget.setLayout(layout)

        layout.addWidget(qt.QLabel("Waiting time between observations (in s)"))
        self._qsbLoopTimeBreak = qt.QSpinBox(parent=widget)
        self._qsbLoopTimeBreak.setMinimum(1)
        self._qsbLoopTimeBreak.setMaximum(1000000)
        self._qsbLoopTimeBreak.setValue(self.maxWaitBtwObsLoop)
        self._qsbLoopTimeBreak.valueChanged.connect(self.setWaitTimeBtwLoop)
        layout.addWidget(self._qsbLoopTimeBreak)

        return widget

    def _getInitPath(self):
        initPath = ""
        if "DATADIR" in os.environ:
            initPath = os.environ["DATADIR"]
            self._qlInfo.setText(
                "note : environment variable DATADIR found, "
                "$DATADIR setted has the root of the observe folder"
            )
            myFont = self._qlInfo.font()
            myFont.setItalic(True)
            self._qlInfo.setFont(myFont)
        else:
            self._qlInfo.setText(
                "note : no DATADIR environment variable setted. "
                "Can't set a default root directory for observation"
            )
            myFont = self._qlInfo.font()
            myFont.setItalic(True)
            self._qlInfo.setFont(myFont)
        return initPath

    def getHistoryWindow(self):
        if self._historyWindow is None:
            self._historyWindow = history.ScanHistory(parent=self)
        return self._historyWindow

    def stop(self, sucess=False):
        """
        Stop the thread of observation

        :param bool sucess: if True this mean that we are stopping the
                            observation because we found an acquisition
                            finished. In this case we don't want to update the
                            status and the log message.

        :return bool: True if the observation have been stopped. Otherwise this
            mean that not observation was executing
        """
        if self.isObserving is False:
            return False

        self._setIsObserving(False)
        if self.loopObservationThread is not None:
            self.loopObservationThread.wait(int(self.maxWaitBtwObsLoop + 2))
        if self.observationThread is not None:
            # remove connection
            self._disconnectObserverThread()
            self.observationThread.blockSignals(True)
            self.observationThread.wait()

        if sucess is False:
            self._setCurrentStatus(str("not processing"))

            if sucess is False:
                if self._observationWidget is not None:
                    self._observationWidget.clear()
                message = "observation stopped"
                self.sigObservationEnd.emit()
                logger.inform(message)
                self.statusBar.showMessage(message)
                self._setCurrentStatus("not processing")
            return True

    def start(self):
        """
        Start the thread of observation

         :return bool: True if the observation was started. Otherwise this
            mean that an observation was already running
        """
        if _DataWatcher.start(self):
            mess = "start observation on %s" % self.folderObserved
            logger.inform(mess)
            self.statusBar.showMessage(mess)
            self._setCurrentStatus("started")
            self.sigObservationStart.emit()
            return True
        else:
            return False

    def _setIsObserving(self, b):
        _DataWatcher._setIsObserving(self, b)
        if _DataWatcher.isObserving(self) is True:
            self._qpbstartstop.setText(self._textStopObservation)
        else:
            self._qpbstartstop.setText(self._textStartObservation)

    def _getFolderSelection(self):
        """
        Return the widget used for the folder selection
        """
        widget = qt.QWidget(self)
        layout = qt.QHBoxLayout()

        self._qtbSelectFolder = qt.QPushButton("Select folder", parent=widget)
        self._qtbSelectFolder.setAutoDefault(True)
        self._qtbSelectFolder.clicked.connect(self._setFolderPath)

        self._qteFolderSelected = qt.QLineEdit("", parent=widget)
        self._qteFolderSelected.textChanged.connect(self._updateFolderObserved)
        self._qteFolderSelected.editingFinished.connect(self._restartObservation)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._qteFolderSelected)
        layout.addWidget(self._qtbSelectFolder)

        self.animated_icon = silxicons.getWaitIcon()
        self.__stateLabel = qt.QLabel(parent=widget)
        self.animated_icon.register(self.__stateLabel)
        self._setStateIcon(silxicons.getQIcon("remove"))

        self.__stateLabel.setFixedWidth(30)
        layout.addWidget(self.__stateLabel)

        widget.setLayout(layout)
        return widget

    def _setFolderPath(self):
        """
        Ask the user the path to the folder to observe
        """
        defaultDirectory = self.getFolderObserved()
        if defaultDirectory is None or not os.path.isdir(defaultDirectory):
            if os.path.isdir(self.DEFAULT_DIRECTORY):
                defaultDirectory = self.DEFAULT_DIRECTORY
            if defaultDirectory is None:
                defaultDirectory = get_default_directory()

        dialog = qt.QFileDialog(self, directory=defaultDirectory)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return

        self.setFolderObserved(dialog.selectedFiles()[0])

        if self.isObserving:
            self._restartObservation()

    def _updateFolderObserved(self, txt):
        self.folderObserved = self._qteFolderSelected.text()
        self.sigFolderObservedChanged.emit()

    def setFolderObserved(self, path):
        if path is not None and os.path.isdir(path):
            super(DataWatcherWidget, self).setFolderObserved(os.path.abspath(path))
            self._qteFolderSelected.setText(self.folderObserved)

    def setStartByOldest(self, b):
        """
        Set if we want to start parsing files from the oldest or the newest

        :param b:
        """
        _DataWatcher.setStartByOldest(self, b)
        self.getConfigWindow()._qcboldest.setChecked(self.startByOldest)

    def _initObservation(self):
        """
        Init the thread running the data watcher functions
        """
        if _DataWatcher._initObservation(self) is True:
            if self._observationWidget is not None:
                self._observationWidget.setOnGoingObservations(
                    self.observationThread.observations
                )
            return True
        else:
            return False

    def _messageNotDir(self, dir):
        super()._messageNotDir(dir=dir)
        message = "Given path (%s) isn't a directory." % dir
        self.statusBar.showMessage("!!! " + message + "!!!")

    def informationReceived(self, info):
        self.statusBar.showMessage(info)

    def _scanStatusChanged(self, scan, status):
        mess = "scan %s is observed. Status: %s" % (os.path.basename(scan), status)
        self.statusBar.showMessage(mess)

    def _connectObserverThread(self):
        if self.observationThread is not None and self.obsThIsConnected is False:
            self.observationThread.observations.sigObsStatusReceived.connect(
                self._scanStatusChanged
            )
            self.observationThread.sigScanReady.connect(self._signalScanReady)
            self.obsThIsConnected = True

    def _disconnectObserverThread(self):
        if self.observationThread is not None and self.obsThIsConnected is True:
            self.observationThread.observations.sigObsStatusReceived.disconnect(
                self._scanStatusChanged
            )
            self.observationThread.sigScanReady.disconnect(self._signalScanReady)
            self.obsThIsConnected = False

    def _initStatusView(self):
        """
        The status view need a thread to update the animated icon when scanning
        """
        self.__threadAnimation = QWaiterThread(0.1)
        self.__threadAnimation.finished.connect(self._updateAnimatedIcon)

    def _updateStatusView(self):
        """Update the processing state"""
        if self.currentStatus in self._animatedStates:
            if not self.__threadAnimation.isRunning():
                self.__threadAnimation.start()
            elif self.__threadAnimation is not None:
                self.__threadAnimation.wait()
        elif self.currentStatus == "acquisition ended":
            self._setStateIcon(silxicons.getQIcon("selected"))
        elif self.currentStatus == "failure":
            self._setStateIcon(silxicons.getQIcon("remove"))
        elif self.currentStatus == "not processing":
            self._setStateIcon(None)

    def _setStateIcon(self, icon):
        """set the icon pass in parameter to the state label

        :param icon:the icon to set"""
        # needed for heritage from DataWatcher
        if icon is None:
            self.__stateLabel.setPixmap(qt.QIcon().pixmap(30, state=qt.QIcon.On))
        else:
            self.__stateLabel.setPixmap(icon.pixmap(30, state=qt.QIcon.On))

    def _updateAnimatedIcon(self):
        """Simple function which manage the waiting icon"""
        if self.currentStatus in self._animatedStates:
            icon = self.animated_icon.currentIcon()
            if icon is None:
                icon = qt.QIcon()
            self.animated_icon._updateState()
            self._setStateIcon(icon)

            # get ready for the next animation
            self.__threadAnimation.start()

    def _signalScanReady(self, scan):
        if type(scan) is str:
            try:
                _scan = ScanFactory.create_scan_object(scan_path=scan)
            except Exception as e:
                logger.error(
                    "Fail to create a TomoBase instance from", scan, "Reason is", e
                )
                return
        else:
            assert isinstance(scan, TomwerScanBase)
            _scan = scan

        _DataWatcher._signalScanReady(self, _scan)
        self.lastFoundScans.add(_scan)
        self._updateLastReceived()

    def _updateLastReceived(self):
        """
        For now we are updating each time the list.
        It would be better to update it instead.
        """
        self.getHistoryWindow().update(scans=list(self.lastFoundScans.items()))

    def _getObservationClass(self):
        return _QOngoingObservation

    def _createDataWatcher(self):
        self.observationThread = _QDataWatcherObserver(
            observationClass=self._getObservationClass(),
            obsMethod=self.obsMethod,
            srcPattern=self.srcPattern,
            destPattern=self.destPattern,
        )
        self._connectObserverThread()

    def _check_finished_scan(self):
        # nothing to do: managed by signals
        pass

    def waitForObservationFinished(self):
        if self.observationThread.observations is not None:
            for dir, thread in self.observationThread.observations.dict.items():
                thread.wait(10)

    def _launchObservation(self):
        """Main function of the widget"""
        if self.isObserving is False:
            return

        # manage data watcher observation
        if self.observationThread is None or not self.observationThread.isRunning():
            if self._initObservation() is False:
                self.currentStatus = self._setCurrentStatus("failure")
                logger.info(
                    "failed on observation",
                    extra={logconfig.DOC_TITLE: self._scheme_title},
                )
                return

        # starting the observation thread
        self.observationThread.start()

        # manage observation loop
        if self.loopObservationThread is None:
            self.loopObservationThread = QWaiterThread(
                self.getTimeBreakBetweenObservation()
            )
            self.loopObservationThread.finished.connect(self._launchObservation)

        if not self.loopObservationThread.isRunning():
            self._connectObserverThread()
            self.loopObservationThread.start()

    def _observation_thread_running(self):
        return self.observationThread is not None and self.observationThread.isRunning()


if __name__ == "__main__":
    qapp = qt.QApplication([])
    widget = DataWatcherWidget(parent=None)
    widget.show()
    qapp.exec_()
