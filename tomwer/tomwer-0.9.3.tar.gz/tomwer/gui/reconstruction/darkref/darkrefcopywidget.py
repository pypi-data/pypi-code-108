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
__date__ = "13/08/2021"


import os
import logging
from silx.gui import qt
from tomwer.core.process.reconstruction.darkref.settings import (
    DARKHST_PREFIX,
    REFHST_PREFIX,
)
from tomwer.io.utils import get_default_directory
from tomwer.core import settings
from tomwer.core import utils
from tomwer.gui.reconstruction.darkref.darkrefwidget import DarkRefWidget

_logger = logging.getLogger(__name__)


class DarkRefAndCopyWidget(DarkRefWidget):
    """
    Widget associated to the DarkRefCopy process
    """

    sigModeAutoChanged = qt.Signal()
    """Signal emitted when the mode auto change"""
    sigCopyActivationChanged = qt.Signal()
    """Signal emitted when the copy is activated or deactivated"""

    def __init__(self, parent=None, reconsparams=None, process_id=None):
        DarkRefWidget.__init__(
            self, parent=parent, reconsparams=reconsparams, process_id=process_id
        )
        self._mode_auto = True

        self._refCopyWidget = RefCopyWidget(parent=self, refCopy=self)
        iCopy = self.mainWidget.addTab(self._refCopyWidget, "copy")
        tooltip = (
            "When copy is activated it will record refHST and dark "
            "files. \n Then when an acquisition without dark or refHST "
            "go through the widget it will copy those dark and refHST "
            "in the acquisition."
        )
        self.mainWidget.setTabToolTip(iCopy, tooltip)
        self.layout().setContentsMargins(0, 0, 0, 0)

        # connect signal / slot
        self._refCopyWidget.sigModeAutoChanged.connect(self._triggerModeAuto)
        self._refCopyWidget.sigCopyActivationChanged.connect(
            self._triggerCopyActivation
        )

    def set_mode_auto(self, auto):
        self._mode_auto = auto

    def setRefsFromScan(self, value):
        raise NotImplementedError()

    def hasFlatStored(self):
        raise NotImplementedError()

    def hasDarkStored(self):
        raise NotImplementedError()

    def clearRef(self):
        raise NotImplementedError()

    def _triggerModeAuto(self, *args, **kwargs):
        self.sigModeAutoChanged.emit()

    def _triggerCopyActivation(self, *args, **kwargs):
        self.sigCopyActivationChanged.emit()

    def setCopyActive(self, active):
        self._refCopyWidget.setChecked(active)

    def isCopyActive(self):
        return self._refCopyWidget.isChecked()

    def setModeAuto(self, mode_auto):
        old = self.blockSignals(True)
        self._refCopyWidget.setModeAuto(mode_auto)
        self.blockSignals(old)

    def isOnModeAuto(self):
        return self._refCopyWidget.is_on_mode_auto()

    def close(self):
        self.blockSignals(True)
        self._refCopyWidget.close()
        super(DarkRefAndCopyWidget, self).close()

    def _dealWithMissingRef(self, scanID):
        # Security: if lbs is full, skip requesting fir user ref
        if (
            settings.isOnLbsram(scanID)
            and utils.isLowOnMemory(settings.get_lbsram_path()) is True
        ):
            # if computer is running into low memory on lbsram skip it
            mess = (
                "low memory, do not ask user for references (refCopy) "
                "for %s" % scanID
            )
            _logger.processSkipped(mess)
            return
        if self._gui.askForRefFolder() is False:
            mes = "no reference created for %s, no link registred." % scanID
            _logger.processSkipped(mes)
        else:
            # process ref on this folder if only originals are here
            self.worker.set_process_only_dkRf(True)
            originalFolder = self.worker.directory
            self.worker.directory = self._gui.getCopyFolder()
            self.worker.process()
            self.worker.set_refs_from_scan(self.worker.directory)
            self.worker.directory = originalFolder

            if self.worker.has_flat_or_dark_stored() is True:
                self.worker.set_process_only_copy(True)
                self.worker.run()
            else:
                self._dealWithMissingRef(scanID)


class RefCopyWidget(qt.QGroupBox):
    """
    GUI for the :class:RefCopy
    """

    sigModeAutoChanged = qt.Signal()
    """Signal emitted when the mode auto change"""
    sigCopyActivationChanged = qt.Signal()
    """Signal emitted when the copy is activated or deactivated"""

    _DEFAULT_DIRECTORY = "/lbsram/data/visitor"
    """Default directory used when the user need to set path to references"""

    _MSG_NO_REF = "!!! No reference recorded !!!"

    def __init__(self, parent, refCopy):
        """

        :param parent: Qt parent
        :param refCopy: instance that inherits from :DarkRefCopy
        """
        qt.QGroupBox.__init__(self, "activate", parent)
        self._refCopy = refCopy
        self.setLayout(qt.QVBoxLayout())
        self.setCheckable(True)
        self.layout().addWidget(self.__createScanPathGUI())
        self.layout().addWidget(self.__createPrefixGUI())
        self.layout().addWidget(self.__createManualGUI())
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)
        self.layout().addWidget(self.__createStatusBarGUI())

        self.setModeAuto(True)
        self._qcbAutoMode.toggled.connect(self._updateModeAuto)
        self._qleScanPath.textEdited.connect(self.setRefsFromScan)

        # expose API
        self.sigActivated = self.toggled

        # connect signal / slot
        self.toggled.connect(self._triggerCopyActivated)
        self._qcbAutoMode.toggled.connect(self._triggerModeAutoChanged)

    def _triggerCopyActivated(self, *args, **kwargs):
        self.sigCopyActivationChanged.emit()

    def _triggerModeAutoChanged(self, *args, **kwargs):
        self.sigModeAutoChanged.emit()

    def sizeHint(self):
        return qt.QSize(400, 200)

    def __createScanPathGUI(self):
        self._folderWidget = qt.QWidget(parent=self)
        self._folderWidget.setLayout(qt.QHBoxLayout())
        self._qtbSelectFolder = qt.QPushButton(
            "Select folder", parent=self._folderWidget
        )
        self._qtbSelectFolder.setAutoDefault(True)
        self._qtbSelectFolder.clicked.connect(self.__setFolderPath)
        self._folderWidget.layout().addWidget(self._qtbSelectFolder)
        self._qleScanPath = qt.QLineEdit("", parent=self)
        self._folderWidget.layout().addWidget(self._qleScanPath)
        return self._folderWidget

    def __createManualGUI(self):
        self._manualFolder = qt.QWidget(parent=self)
        self._manualFolder.setLayout(qt.QHBoxLayout())

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self._manualFolder.layout().addWidget(spacer)

        self._qcbAutoMode = qt.QCheckBox(parent=self)
        self._manualFolder.layout().addWidget(self._qcbAutoMode)
        self._manualFolder.layout().addWidget(qt.QLabel("auto"))
        tooltip = (
            "When copy is activated it will record refHST and dark "
            "files. \n Then when an acquisition without dark or refHST "
            "go through the widget it will copy those dark and refHST "
            "in the acquisition. \n"
            "Files are normalized used the `SrCurrent` information.\n"
            "In automatic mode the widget will record the refHST and "
            "dark from the latest acquisition having those. \n"
            "In manual mode user can give a path to an aacquisition "
            "containing those files and set them from it."
        )
        self._manualFolder.setToolTip(tooltip)
        return self._manualFolder

    def __createPrefixGUI(self):
        self._prefixLogger = qt.QWidget(parent=self)
        self._prefixLogger.setLayout(qt.QGridLayout())
        layout = self._prefixLogger.layout()
        layout.addWidget(qt.QLabel("dark prefix:", parent=self), 0, 0)
        self._darkPrefix = qt.QLineEdit(DARKHST_PREFIX, parent=self)
        layout.addWidget(self._darkPrefix, 0, 1)
        layout.addWidget(qt.QLabel("flat prefix:", parent=self), 1, 0)
        self._refPrefix = qt.QLineEdit(REFHST_PREFIX, parent=self)
        layout.addWidget(self._refPrefix, 1, 1)
        return self._prefixLogger

    def __createStatusBarGUI(self):
        self._statusBar = qt.QStatusBar(parent=self)
        self._statusBar.showMessage(self._MSG_NO_REF)
        return self._statusBar

    def _clearRef(self):
        self._refCopy.clear_ref()
        self._refSetted(None)

    def askForRefFolder(self):
        # TODO: should also manage [XXX]tomwer_processes.h5 as input
        dialog = _DialogNoLink(refPrefix=self._refPrefix, darkPrefix=self._darkPrefix)
        if dialog.exec_() == 0:
            return False
        else:
            if dialog.refPrefix != self._refPrefix:
                self.setRefHstPrefix(dialog.refPrefix)
            if dialog.darkPrefix != self._darkPrefix:
                self.setDarkHstPrefix(dialog.darkPrefix)
            if dialog.currentFolder != self._qleScanPath.text():
                self.setRefsFromScan(dialog.currentFolder)
            return True

    def getRefHstPrefix(self):
        self._refCopy.set_refHST_prefix(self, self._refPrefix.text())
        return self._refCopy.refHST_prefix(self)

    def getDarkHstPrefix(self):
        self._refCopy.set_darkHST_prefix(self, self._darkPrefix.text())
        return self._refCopy.darkHST_prefix(self)

    def setDarkHstPrefix(self, prefix):
        self._darkPrefix.setText(prefix)
        self._refCopy.set_darkHST_prefix(self, prefix)

    def setRefHstPrefix(self, prefix):
        self._refPrefix.setText(prefix)
        self._refCopy.set_refHST_prefix(self, prefix)

    def __setFolderPath(self):
        defaultDirectory = get_default_directory
        if os.path.isdir(self._DEFAULT_DIRECTORY):
            defaultDirectory = self._DEFAULT_DIRECTORY

        dialog = qt.QFileDialog(self, directory=defaultDirectory)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return

        self.setRefsFromScan(dialog.selectedFiles()[0])

    def getCopyFolder(self):
        return self._qleScanPath.text()

    def setRefsFromScan(self, scanID):
        self._qleScanPath.setText(scanID)
        if self._refCopy.set_refs_from_scan(scanID) is True:
            self._updateRefInformation()
            return True
        else:
            return False

    def setModeAuto(self, b):
        self._refCopy.set_mode_auto(b)
        self._folderWidget.setVisible(not b)
        self._qcbAutoMode.setChecked(b)

    def is_on_mode_auto(self):
        return self._qcbAutoMode.isChecked()

    def _updateModeAuto(self):
        """call back of `_qcbGiveManually`"""
        self._refCopy.set_mode_auto(self._qcbAutoMode.isChecked())
        self._folderWidget.setVisible(not self._qcbAutoMode.isChecked())

    def _updateRefInformation(self):
        if self._refCopy._darkRef.worker.has_flat_or_dark_stored():
            self._refSetted(self._refCopy._darkRef.worker.directory)
        else:
            self._refSetted(None)

    def _refSetted(self, scanID):
        if scanID is None:
            self._statusBar.showMessage(self._MSG_NO_REF)
        else:
            msg = "Has reference recorded from " + str(scanID)
            self._statusBar.showMessage(msg)

    def copyActivated(self):
        """

        :return bool: Return True if the user want to aply the dark ref copy
        """
        return self.isChecked()


class _DialogNoLink(qt.QDialog):
    """A QDialog widget to aks the user to set the path to the reference link
    or to skip the reference copy creation.

    Behavior is:

    * if the dialog has no folder set will ask for one
    * if the dialog has a folder ask for a new one or to change the prefix
    """

    _TIMEOUT = 60000  # ms
    _UPDATE_DIALOG_EACH = 1000  # ms

    def __init__(
        self,
        parent=None,
        title="Path to scan references",
        currentFolder=None,
        refPrefix=None,
        darkPrefix=None,
    ):
        qt.QDialog.__init__(self, parent)
        assert refPrefix
        assert darkPrefix
        self.path = None
        if currentFolder and os.path.isdir(currentFolder):
            self.currentFolder = currentFolder
        else:
            self.currentFolder = None
        self.refPrefix = refPrefix
        self.darkPrefix = darkPrefix
        self._restingTime = self._TIMEOUT + self._UPDATE_DIALOG_EACH  # in sec

        self._title = title
        self.setWindowTitle(title)
        self.setLayout(qt.QVBoxLayout())

        self._msgLabel = qt.QLabel("")
        self.layout().addWidget(self._msgLabel)
        # define the buttons
        types = qt.QDialogButtonBox.Ignore

        self._buttonsModal = qt.QDialogButtonBox(parent=self)
        self._buttonsModal.setStandardButtons(types)
        self.layout().addWidget(self._buttonsModal)
        self._buttonsModal.button(qt.QDialogButtonBox.Ignore).clicked.connect(
            self.reject
        )

        self._setFolderButton = qt.QPushButton("", parent=self)
        self._buttonsModal.addButton(
            self._setFolderButton, qt.QDialogButtonBox.ActionRole
        )
        self._updateMsg()

        self._setFolderButton.clicked.connect(self._setScanDir)

        if self.currentFolder is not None:
            self._changePrefixButton = qt.QPushButton("change prefix", parent=self)
            self._buttonsModal.addButton(
                self._changePrefixButton, qt.QDialogButtonBox.ActionRole
            )
            self._changePrefixButton.clicked.connect(self._changePrefix)

        self.setModal(False)

        # create a timer to close (and ignore) automatically this to be blocking
        # for the workflow
        self._infoRestTime = qt.QTimer()
        self._infoRestTime.timeout.connect(self._updateRestingTime)
        self._updateRestingTime()

    def _updateMsg(self):
        if self.currentFolder is None:
            text = (
                "No references registered. \n"
                "To create copy to reference file please give path to "
                "a folder containing those files. \n"
                "Will ignore automatically in %s (sec))" % (self._restingTime / 1000)
            )
            textSetFolder = "Set scan directory"
        else:
            text = (
                "No references found in %s. Please change directory or "
                "dark/ref prefix \n"
                "Will ignore automatically in %s (sec))" % (self._restingTime / 1000)
            )
            textSetFolder = "Change scan directory"
        self._msgLabel.setText(text)
        self._setFolderButton.setText(textSetFolder)

    def _updateRestingTime(self):
        self._restingTime = self._restingTime - self._UPDATE_DIALOG_EACH
        if self._restingTime <= 0.0:
            self.close()
            return

        title = self._title + " (will ignore automatically in %s (sec))" "" % (
            self._restingTime / 1000
        )  # dispaly in sec
        self._updateMsg()
        self.setWindowTitle(title)
        self._infoRestTime.start(1000)  # in micro second

    def _changePrefix(self):
        diag = _PrefixDialog(
            parent=self, refPrefix=self.refPrefix, darkPrefix=self.darkPrefix
        )
        if diag.exec_():
            self.refPrefix = diag.refPrefix
            self.darkPrefix = diag.darkPrefix
            self.accept()

    def _setScanDir(self):
        defaultDirectory = get_default_directory()
        if os.path.isdir(RefCopyWidget._DEFAULT_DIRECTORY):
            defaultDirectory = RefCopyWidget._DEFAULT_DIRECTORY

        dialog = qt.QFileDialog(self, directory=defaultDirectory)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        res = dialog.exec_()

        if not res:
            dialog.close()
            return

        self.currentFolder = dialog.selectedFiles()[0]
        self.accept()

    def accept(self):
        self._infoRestTime.stop()
        qt.QDialog.accept(self)

    def reject(self):
        self._infoRestTime.stop()
        qt.QDialog.reject(self)


class _PrefixDialog(qt.QDialog):
    def __init__(
        self, parent=None, title="Change prefix", refPrefix=None, darkPrefix=None
    ):
        qt.QDialog.__init__(self, parent)
        self.refPrefix = refPrefix
        self.darkPrefix = darkPrefix
        self.setWindowTitle(title)
        self.setLayout(qt.QVBoxLayout())

        self._mainWidget = qt.QWidget(parent=self)
        self._mainWidget.setLayout(qt.QGridLayout())
        layout = self._mainWidget.layout()
        self.layout().addWidget(self._mainWidget)

        layout.addWidget(qt.QLabel("dark prefix:", parent=self), 0, 0)
        self._darkPrefix = qt.QLineEdit(DARKHST_PREFIX, parent=self)
        layout.addWidget(self._darkPrefix, 0, 1)
        layout.addWidget(qt.QLabel("flat prefix:", parent=self), 1, 0)
        self._refPrefix = qt.QLineEdit(REFHST_PREFIX, parent=self)
        layout.addWidget(self._refPrefix, 1, 1)

        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttonsModal = qt.QDialogButtonBox(parent=self)
        self._buttonsModal.setStandardButtons(types)
        self.setModal(True)
        self.layout().addWidget(self._buttonsModal)

        self._buttonsModal.button(qt.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self._buttonsModal.button(qt.QDialogButtonBox.Cancel).clicked.connect(
            self.reject
        )
