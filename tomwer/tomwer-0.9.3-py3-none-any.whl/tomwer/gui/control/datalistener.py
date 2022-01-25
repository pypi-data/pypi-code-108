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


import os
import weakref
import socket
from silx.gui import qt
from tomwer.core import settings
from tomwer.core.process.utils import LastReceivedScansDict
from tomwer.gui import icons as tomwericons
from tomwer.gui.control import datareacheractions as actions
from tomwer.gui.control.history import ScanHistory
from tomwer.gui.control.observations import ScanObservation
from tomwer.core.scan.blissscan import BlissScan
from tomwer.synctools.rsyncmanager import BlissSequenceRSyncWorker
from tomwer.gui.utils.inputwidget import ConfigFileSelector
from tomwer.gui.utils.inputwidget import NXTomomillOutputDirSelector


class DataListenerWidget(qt.QMainWindow):
    """
    Widget to display the bliss acquisition on going and finished
    """

    NB_STORED_LAST_FOUND = 20

    sigActivate = qt.Signal()
    """Signal emitted when the listening start"""
    sigDeactivate = qt.Signal()
    """Signal emitted when the listening end"""
    sigConfigurationChanged = qt.Signal()
    """Signal emitted when the configuration for the bliss client is updated"""
    sigAcquisitionEnded = qt.Signal(tuple)
    """Signal emitted when an acquisition is ended without errors.
    Tuple contains (master_file, entry, proposal_file)"""
    sigServerStopped = qt.Signal()
    """Signal emitted when the server is stopped by a sigkill or sigterm"""
    sigCFGFileChanged = qt.Signal(str)
    """Signal emitted when path to the nxtomomill configuration file change"""

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self._listener = None
        self.lastFoundScans = LastReceivedScansDict(self.NB_STORED_LAST_FOUND)
        self._blissScans = {}
        # keep a trace of the bliss scans. key is bliss scan strings
        # (used as id), value is BlissScan instance
        self._syncWorkers = {}
        # associate scan path (directory) to the RSyncWorker

        # create widgets
        self._centralWidget = qt.QWidget(parent=self)
        self._centralWidget.setLayout(qt.QVBoxLayout())

        self._controlWidget = DataListenerControl(parent=self)
        """Widget containing the 'control' of the datalistener: start of stop
        the listener"""
        self._centralWidget.layout().addWidget(self._controlWidget)

        self._historyWindow = ScanHistory(parent=self)
        """Widget containing the latest valid scan found by the listener"""
        self._centralWidget.layout().addWidget(self._historyWindow)

        self._configWindow = ConfigurationWidget(parent=self)
        """Widget containing the configuration to communicate with bliss"""
        self._centralWidget.layout().addWidget(self._configWindow)

        self._observationWidget = ScanObservation(parent=self)
        """Widget containing the current observed directory by the listener"""
        self._centralWidget.layout().addWidget(self._observationWidget)

        # create toolbar
        toolbar = qt.QToolBar("")
        toolbar.setIconSize(qt.QSize(32, 32))

        self._controlAction = actions.ControlAction(parent=self)
        self._observationsAction = actions.ObservationAction(parent=self)
        self._configurationAction = actions.ConfigurationAction(parent=self)
        self._historyAction = actions.HistoryAction(parent=self)
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

        # signal / slot connection
        self._actionGroup.triggered.connect(self._updateCentralWidget)
        self._controlWidget.sigActivated.connect(self._activated)
        self._controlWidget.sigDeactivated.connect(self._deactivated)
        self._configWindow.sigConfigurationChanged.connect(self._configChanged)
        self._configWindow.sigCFGFileChanged.connect(self._cfgFileChanged)

        # expose api
        self.activate = self._controlWidget.activate
        self.getCFGFilePath = self._configWindow.getCFGFilePath
        self.getOutputFolder = self._configWindow.getOutputFolder

        # set up
        self.setCentralWidget(self._centralWidget)
        self._controlAction.setChecked(True)
        self._updateCentralWidget(self._controlAction)

    def getHost(self) -> str:
        """Return server host"""
        return self._configWindow.getHost()

    def getPort(self) -> int:
        """Return server port"""
        return self._configWindow.getPort()

    def getBlissServerConfiguration(self) -> dict:
        return self._configWindow.getConfiguration()

    def setBlissServerConfiguation(self, config):
        self._configWindow.setConfiguration(config=config)

    def setCFGFilePath(self, cfg_file):
        self._configWindow.setCFGFilePath(cfg_file)

    def setOutputFolder(self, output_dir):
        self._configWindow.setOutputFolder(output_dir)

    def setListener(self, listener):
        self._listener = weakref.ref(listener, self._cleanConnection)
        self._listener().sigAcquisitionStarted.connect(self._acquisitionStarted)
        self._listener().sigScanAdded.connect(self._acquisitionUpdated)
        self._listener().sigAcquisitionEnded.connect(self._acquisitionEnded)

    def _cleanConnection(self):
        self._listener().sigAcquisitionStarted.disconnect(self._acquisitionStarted)
        self._listener().sigScanAdded.disconnect(self._acquisitionUpdated)
        self._listener().sigAcquisitionEnded.disconnect(self._acquisitionEnded)

    def _activated(self):
        self.sigActivate.emit()

    def _deactivated(self):
        self.sigDeactivate.emit()

    def _configChanged(self):
        self.sigConfigurationChanged.emit()

    def _cfgFileChanged(self, cfg_file):
        self.sigCFGFileChanged.emit(cfg_file)

    def _updateCentralWidget(self, action_triggered):
        action_to_widget = {
            self._controlAction: self._controlWidget,
            self._historyAction: self._historyWindow,
            self._observationsAction: self._observationWidget,
            self._configurationAction: self._configWindow,
        }
        for action, widget in action_to_widget.items():
            widget.setVisible(action is action_triggered)

    def _serverStopped(self):
        self.sigServerStopped.emit()

    def _acquisitionStarted(self, arg: tuple):
        master_file, entry, proposal_file, saving_file = arg
        scan = self._getBlissScan(
            master_file=master_file, entry=entry, proposal_file=proposal_file
        )
        if settings.isOnLbsram(scan.path):
            self._attachRSyncWorker(scan.path, proposal_file, saving_file)
        self.addAcquisitionObserve(scan=scan)

    def _acquisitionEnded(self, arg: tuple):
        master_file, entry, proposal_file, saving_file, succeed = arg
        scan = self._getBlissScan(
            master_file=master_file, entry=entry, proposal_file=proposal_file
        )
        self.setAcquisitionEnded(scan=scan, success=succeed)
        if self._hasRSyncWorkerAttach(scan.path):
            self._detachRSyncWorker(scan.path)
        self.sigAcquisitionEnded.emit(
            (master_file, entry, proposal_file, saving_file, succeed)
        )

    def _acquisitionUpdated(self, arg: tuple):
        master_file, entry, proposal_file, saving_file, scan_number = arg
        scan = self._getBlissScan(
            master_file=master_file, entry=entry, proposal_file=proposal_file
        )
        scan.add_scan_number(scan_number)
        if settings.isOnLbsram(scan.path):
            if not self._hasRSyncWorkerAttach(scan.path):
                self._attachRSyncWorker(
                    scan.path, proposal_file=proposal_file, saving_file=saving_file
                )

        self.updateAcquisitionObserve(scan=scan)

    def _getBlissScan(self, master_file, entry, proposal_file):
        scan_id = BlissScan.get_id_name(master_file=master_file, entry=entry)
        if scan_id in self._blissScans:
            return self._blissScans[scan_id]
        else:
            bliss_scan = BlissScan(
                master_file=master_file, entry=entry, proposal_file=proposal_file
            )
            self._blissScans[str(bliss_scan)] = bliss_scan
            return bliss_scan

    def addAcquisitionObserve(self, scan):
        self._observationWidget.addObservation(scan)
        self._observationWidget.update(scan, "on going")

    def setAcquisitionEnded(self, scan, success):
        if success is False:
            self._observationWidget.update(scan, "failed")
        else:
            self._observationWidget.removeObservation(scan)
            self.lastFoundScans.add(scan)
            self._historyWindow.update(list(self.lastFoundScans.items()))

    def updateAcquisitionObserve(self, scan):
        self._observationWidget.update(scan, "on going")

    def sizeHint(self):
        return qt.QSize(600, 400)

    def _attachRSyncWorker(self, scan_path, proposal_file, saving_file):
        dest_dir = scan_path.replace(
            settings.get_lbsram_path(), settings.get_dest_path()
        )
        dest_dir = os.path.dirname(dest_dir)
        if proposal_file is not None:
            dest_proposal_file = proposal_file.replace(
                settings.get_lbsram_path(), settings.get_dest_path()
            )
        else:
            dest_proposal_file = None
        if saving_file is not None:
            dest_saving_file = saving_file.replace(
                settings.get_lbsram_path(), settings.get_dest_path()
            )
        else:
            dest_saving_file = None
        worker = BlissSequenceRSyncWorker(
            src_dir=scan_path,
            dst_dir=dest_dir,
            delta_time=1,
            src_proposal_file=proposal_file,
            dst_proposal_file=dest_proposal_file,
            src_sample_file=saving_file,
            dst_sample_file=dest_saving_file,
        )
        self._syncWorkers[scan_path] = worker
        worker.start()

    def _detachRSyncWorker(self, scan_path):
        if self._hasRSyncWorkerAttach(scan_path=scan_path):
            worker = self._syncWorkers[scan_path]
            worker.stop()
            del self._syncWorkers[scan_path]

    def _hasRSyncWorkerAttach(self, scan_path):
        return scan_path in self._syncWorkers


class DataListenerControl(qt.QWidget):
    """Interface to control the activation of the datalistener"""

    sigActivated = qt.Signal()
    """signal emitted when the datalistener is start"""
    sigDeactivated = qt.Signal()
    """signal emitted when the datalistener is stop"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QGridLayout())

        # add left spacer
        lspacer = qt.QWidget(self)
        lspacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(lspacer, 0, 0, 1, 1)

        # add start / stop icon frame
        self._iconLabel = qt.QLabel(parent=self)
        self._iconLabel.setMinimumSize(qt.QSize(55, 55))
        self.layout().addWidget(self._iconLabel, 0, 1, 1, 1)

        # add button
        self._button = qt.QPushButton(self)
        self.layout().addWidget(self._button, 1, 1, 1, 1)

        # add right spacer
        rspacer = qt.QWidget(self)
        rspacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(rspacer, 0, 2, 1, 1)

        # bottom spacer
        bspacer = qt.QWidget(self)
        bspacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(bspacer, 2, 1, 1, 1)

        # set up
        self._updateIconAndText(activate=False)

        # connect signal / slot
        self._button.released.connect(self._buttonCallback)

    def _buttonCallback(self):
        self.activate(not self.isActivate())

    def isActivate(self):
        return self._button.text() == "stop"

    def activate(self, activate=True):
        self._updateIconAndText(activate=activate)
        if activate is True:
            self.sigActivated.emit()
        else:
            self.sigDeactivated.emit()

    def _updateIconAndText(self, activate):
        if activate:
            icon = tomwericons.getQIcon("datalistener_activate")
        else:
            icon = tomwericons.getQIcon("datalistener_deactivate")

        text = "stop" if activate else "start"
        self._button.setText(text)
        self._iconLabel.setPixmap(icon.pixmap(80, 80))


class ConfigurationWidget(qt.QDialog):
    """Widget for data listener configuration"""

    sigConfigurationChanged = qt.Signal()
    """Signal emitted when the configuration change"""

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        # host
        self._hostLabel = qt.QLabel("host", self)
        self.layout().addWidget(self._hostLabel, 0, 0, 1, 1)
        self._hostQLE = qt.QLineEdit("", self)
        self._hostQLE.setReadOnly(True)
        self.layout().addWidget(self._hostQLE, 0, 1, 1, 1)

        # port
        self._portLabel = qt.QLabel("port", self)
        self.layout().addWidget(self._portLabel, 1, 0, 1, 1)
        self._portSpinBox = qt.QSpinBox(self)
        self._portSpinBox.setMinimum(0)
        self._portSpinBox.setMaximum(100000)
        self._portSpinBox.setReadOnly(True)
        self.layout().addWidget(self._portSpinBox, 1, 1, 1, 2)

        # configuration file to use
        self._cfgLabel = qt.QLabel("config file")
        self.layout().addWidget(self._cfgLabel, 2, 0, 1, 1)
        self._cfgWidget = ConfigFileSelector(self)
        self._cfgWidget.setContentsMargins(0, 0, 0, 0)
        self._cfgWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._cfgWidget, 2, 1, 1, 2)
        tooltip = (
            "You can provide a configuration file to tune conversion "
            "done by nxtomomill. If None is provided then the default "
            "parameters will be used."
        )
        self._cfgLabel.setToolTip(tooltip)
        self._cfgWidget.setToolTip(tooltip)

        # output folder
        self._outputFolderLabel = qt.QLabel("nexus file output dir")
        self.layout().addWidget(self._outputFolderLabel, 3, 0, 1, 1)
        self._nxTomomillOutputWidget = NXTomomillOutputDirSelector(self)
        self._nxTomomillOutputWidget.setContentsMargins(0, 0, 0, 0)
        self._nxTomomillOutputWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._nxTomomillOutputWidget, 3, 1, 1, 2)

        # buttons
        types = qt.QDialogButtonBox.Apply
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)
        self._buttons.button(qt.QDialogButtonBox.Apply).setToolTip(
            "Once apply if a listening is on going"
            "then it will stop the current listening and"
            "restart it with the new parameters"
        )
        self.layout().addWidget(self._buttons, 5, 0, 1, 3)

        # height spacer
        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 6, 0, 1, 1)

        # expose API
        self.sigCFGFileChanged = self._cfgWidget.sigConfigFileChanged

        # connect signal / slot
        self._buttons.button(qt.QDialogButtonBox.Apply).clicked.connect(self.validate)
        self._nxTomomillOutputWidget.sigChanged.connect(self.validate)

        # set up
        self._buttons.hide()
        if settings.JSON_RPC_HOST is None:
            self.setHost(socket.gethostname())
        else:
            self.setHost(settings.JSON_RPC_HOST)
        self.setPort(settings.JSON_RPC_PORT)

    def getCFGFilePath(self):
        return self._cfgWidget.getCFGFilePath()

    def setCFGFilePath(self, cfg_file):
        self._cfgWidget.setCFGFilePath(cfg_file)

    def getOutputFolder(self):
        return self._nxTomomillOutputWidget.getOutputFolder()

    def setOutputFolder(self, output_dir):
        self._nxTomomillOutputWidget.setOutputFolder(output_dir)

    def addBlissSession(self, session: str) -> None:
        if self._blissSession.findText(session) >= 0:
            return
        else:
            self._blissSession.addItem(session)

    def getConfiguration(self) -> dict:
        return {"host": self.getHost(), "port": self.getPort()}

    def setConfiguration(self, config: dict):
        if "host" in config:
            self.setHost(config["host"])
        if "port" in config:
            self.setPort(config["port"])

    def getHost(self) -> str:
        return self._hostQLE.text()

    def setHost(self, name: str):
        self._hostQLE.setText(name)

    def getPort(self) -> int:
        return self._portSpinBox.value()

    def setPort(self, port: int) -> None:
        assert isinstance(port, int)
        self._portSpinBox.setValue(port)

    def validate(self):
        self.sigConfigurationChanged.emit()
