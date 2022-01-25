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
__date__ = "24/01/2017"

from silx.gui import qt
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui import stackplot
from tomwer.io.utils import get_default_directory
import os

import logging

logger = logging.getLogger(__name__)


class ScanWidget(qt.QWidget):
    """
    Widget to display all scan information

    :param parent: the qt parent of the widget
    :param canLoadOtherScan: can we load an other scan
    """

    def __init__(self, parent=None, canLoadOtherScan=False):

        qt.QWidget.__init__(self, parent)
        self.ftseriereconstruction = None

        self.canLoadOtherScan = canLoadOtherScan
        self.__loadGUI()

    def __loadGUI(self):
        """Function loading the GUI. Not done on the constructor to avoid memory
        charge
        """

        layout = qt.QVBoxLayout()
        # add the scan ID label or folder getter
        self._folderSelection = self.__createFolderSelection()
        self._folderSelection.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        layout.addWidget(self._folderSelection)
        # create viewers
        self.stackImageViewerTab = qt.QTabWidget(self)
        self.stackImageViewerTab.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding
        )
        layout.addWidget(self.stackImageViewerTab)
        self.setLayout(layout)

        self.stackImageViewerTab.setLayout(qt.QVBoxLayout())
        self.stackImageViewerTab.layout().setContentsMargins(0, 0, 0, 0)
        self._stackImageViewerScan = stackplot._QImageFileStackPlot(self)
        # self._stackImageViewerScan.setTranspose(True)
        self.stackImageViewerTab.addTab(self._stackImageViewerScan, "Reconstruction")

        self._stackImageViewerRadio = stackplot._QImageFileStackPlot(self)
        self.stackImageViewerTab.addTab(self._stackImageViewerRadio, "Radios")

        self.loaded = True

    def __createFolderSelection(self):
        layoutScanId = qt.QHBoxLayout()
        widget = qt.QWidget(self)
        widget.setLayout(layoutScanId)
        self.folderName = qt.QLineEdit(widget)
        layoutScanId.addWidget(self.folderName)
        self.button = qt.QPushButton("Select folder", parent=widget)
        self._rootFolderSelection = None
        layoutScanId.addWidget(self.button)
        self.button.clicked.connect(self._getFolder)
        # self.folderName.textChanged.connect(self._loadNewSerie)

        if not self.canLoadOtherScan:
            self.button.hide()
            self.folderName.setEnabled(False)

        return widget

    def setRootFolderSelection(self, path):
        """Set the path open when selection a folder to be diaplyed

        :param str path: root path to be open when asking for a new folder
        """
        self._rootFolderSelection = path

    def getCurrentScanFolder(self):
        """Return the folder we want to scan"""
        return self.folderName.text()

    def _loadNewSerie(self, scan):
        """
        Load a new serie from the given scan

        :param TomwerScanBase scan: scan to be displayed
        """
        if scan is None:
            return
        assert isinstance(scan, TomwerScanBase)
        self.updateData(scan)

    def updateData(self, scan):
        """
        Update the current ftSerieReconstruction displayed

        :param FtserieReconstruction scan: the new serie to be
        displayed
        """
        if scan is None or scan.path is None:
            return

        assert type(scan.path) is str

        self.ftseriereconstruction = scan
        self.ftseriereconstruction.update()
        self.loaded = False
        self.folderName.setText(str(scan))
        self._stackImageViewerRadio.setImages(self.ftseriereconstruction.projections)
        self._stackImageViewerScan.setImages(
            self.ftseriereconstruction.get_reconstructions_urls()
        )

    def _getFolder(self):
        """
        Call back when the user want to change the folder to validate
        """

        defaultDirectory = self._rootFolderSelection or get_default_directory()
        currentSettedFolder = self.getCurrentScanFolder()

        if currentSettedFolder is not None and os.path.isdir(currentSettedFolder):
            defaultDirectory = currentSettedFolder

        dialog = qt.QFileDialog(self, directory=defaultDirectory)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return None

        self.folderName.setText(dialog.selectedFiles()[0])

    def clear(self):
        self.ftseriereconstruction = None

        self.loaded = False
        self.folderName.setText("")
        self._stackImageViewerRadio.clear()
        self._stackImageViewerScan.clear()

    def showActiveImage(self):
        self._stackImageViewerRadio.updateActiveImage()
        self._stackImageViewerScan.updateActiveImage()


class ScanWidgetValidation(ScanWidget):
    """
    This is the same as ScanWidget but include a widget button which will
    emit signals such as validated, canceled...

    :param parent: the qt parent of the widget
    :param canLoadOtherScan: can we load an other scan
    """

    def __init__(self, parent=None, canLoadOtherScan=False):
        ScanWidget.__init__(self, parent=parent, canLoadOtherScan=canLoadOtherScan)

        self.validationWidget = ValidationWidget(
            parent=self, ftseriereconstruction=self.ftseriereconstruction
        )
        self.validationWidget.setVisible(not canLoadOtherScan)
        self.validationWidget.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )

        self.layout().addWidget(self.validationWidget)

    def updateData(self, scan):
        ScanWidget.updateData(self, scan)
        if scan is not None:
            self.validationWidget.ftseriereconstruction = scan


class ValidationWidget(qt.QGroupBox):
    """
    Class containing all the validation buttons
    and sending signals when they are pushed

    :param QObject parent: the parent of the QTabWidget
    :param :class:`.FtserieReconstruction`: the scan to display
    """

    sigValidateScan = qt.Signal(str)
    sigCancelScan = qt.Signal(str)
    sigRedoAcquisitionScan = qt.Signal(TomwerScanBase)
    sigChangeReconstructionParametersScan = qt.Signal(TomwerScanBase)

    def __init__(self, ftseriereconstruction, parent=None):
        qt.QGroupBox.__init__(self, title="Validate manually", parent=parent)

        self.setCheckable(True)
        self.ftseriereconstruction = ftseriereconstruction
        layout = qt.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        #  validate button
        self.validateButton = qt.QPushButton("Validate")
        style = qt.QApplication.style()
        self.validateButton.setIcon(style.standardIcon(qt.QStyle.SP_DialogApplyButton))
        self.validateButton.pressed.connect(self.__validated)
        layout.addWidget(self.validateButton, 0, 2)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        layout.addWidget(spacer, 0, 1)

        #  cancel button
        self.cancelButton = qt.QPushButton("Cancel")
        self.cancelButton.setIcon(style.standardIcon(qt.QStyle.SP_DialogCancelButton))
        self.cancelButton.pressed.connect(self.__canceled)
        layout.addWidget(self.cancelButton, 0, 0)
        # for now this button is hidden because the behavior haven't been
        # clearly defined
        # self.cancelButton.hide()

        #  change reconstruction parameters button
        self.changeReconsParamButton = qt.QPushButton(
            "Change reconstruction parameters"
        )
        self.changeReconsParamButton.setIcon(
            style.standardIcon(qt.QStyle.SP_FileDialogContentsView)
        )
        self.changeReconsParamButton.pressed.connect(
            self.__updateReconstructionParameters
        )
        layout.addWidget(self.changeReconsParamButton, 2, 0)

    def setEnabled(self, b):
        self.validateButton.setEnabled(b)
        self.cancelButton.setEnabled(b)
        self.changeReconsParamButton.setEnabled(b)

    def __validated(self):
        """Callback when the validate button is pushed"""
        self.sigValidateScan.emit("")

    def __canceled(self):
        """Callback when the cancel button is pushed"""
        if self.ftseriereconstruction is not None:
            self.setEnabled(False)
            self.sigCancelScan.emit(self.ftseriereconstruction.path)

    def __redoacquisition(self):
        """Callback when the redo acquisition button is pushed"""
        if self.ftseriereconstruction is not None:
            self.setEnabled(False)
            self.sigRedoAcquisitionScan.emit(self.ftseriereconstruction)

    def __updateReconstructionParameters(self):
        """Callback when the change reconstruction button is pushed"""
        if self.ftseriereconstruction is not None:
            self.setEnabled(False)
            self.sigChangeReconstructionParametersScan.emit(self.ftseriereconstruction)


class ImageStackViewerValidator(ScanWidgetValidation):
    """
    Widget to visualize a stack of image

    :param QObject parent: the parent of the QTabWidget
    :param :class:`.FtserieReconstruction`: the scan to display
    """

    _sizeHint = qt.QSize(600, 600)

    def __init__(self, parent=None, ftseries=None):
        ScanWidgetValidation.__init__(self, parent)

        self._scanWidgetLayout = qt.QVBoxLayout()
        self.layout().setContentsMargins(0, 0, 0, 0)

        if ftseries is not None:
            self.addScan(ftseries)

    def addScan(self, ftseriereconstruction, entry=None):
        """function called for showing infomration about a new reconstruction

        :param FtserieReconstruction ftseriereconstruction:
            contains all information about the reconstruciton (scan path,
            reconstruction path ... )
        """
        if not type(ftseriereconstruction) is TomwerScanBase:
            raise RuntimeError(
                "Update error can't manage a type different than\
                                 FtserieReconstruction"
            )

        assert ftseriereconstruction is not None
        assert ftseriereconstruction.path is not None

        logger.info(
            "Scan validator received %s to be validated" % ftseriereconstruction.path
        )

        self.lastReconstructionReceived = ftseriereconstruction
        self._updateData(self.lastReconstructionReceived)

    def updateFromPath(self, path, entry=None):
        """Show the reconstruction from a path"""
        if not os.path.isdir(path):
            raise RuntimeError("givem path %s is not a directory" % path)

        self.addScan(ScanFactory.create_scan_object(path, entry=entry))

    def __updateScanTabsID(self):
        if hasattr(self, "lastReconstructionReceived") and (
            self.lastReconstructionReceived is not None
        ):
            # update FtSerie in scan to treat tab
            self.updateData(self.lastReconstructionReceived)
            # update folder path in other tab
            assert self.OTHER_TAB in self.tabsWidget
            if self.lastReconstructionReceived.path is not None:
                self.setRootFolderSelection(
                    os.path.dirname(self.lastReconstructionReceived.path)
                )

    def sizeHint(self):
        """Return a reasonable default size for usage in :class:`PlotWindow`"""
        return self._sizeHint


def setUp():
    import fabio.edfimage
    import tempfile
    import numpy

    folder = tempfile.mkdtemp()
    basename = os.path.basename(folder)

    # create projections
    for i in range(20):
        f = tempfile.mkstemp(
            prefix=basename, suffix=str("_" + str(i) + ".edf"), dir=folder
        )
        data = numpy.array(numpy.random.random(200 * 200))
        data.shape = (200, 200)
        edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
        edf_writer.write(f[1])

    # create reconstruction
    for i in range(5):
        f = tempfile.mkstemp(
            prefix=basename, suffix=str("_slice_" + str(i) + ".edf"), dir=folder
        )
        data = numpy.zeros((200, 200))
        data[:: i + 2, :: i + 2] = 1.0
        edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
        edf_writer.write(f[1])

    f = tempfile.mkstemp(
        prefix=basename, suffix=str("_slice_" + str(6) + ".edf"), dir=folder
    )
    data = numpy.zeros((200, 200))
    data[50:150, 50:150] = 1.0
    edf_writer = fabio.edfimage.EdfImage(data=data, header={"tata": "toto"})
    edf_writer.write(f[1])

    return folder
