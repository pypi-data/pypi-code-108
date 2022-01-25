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
"""
contains gui relative frame difference display
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/12/2021"


import functools
import logging
import os
import numpy
from processview.core.dataset import DatasetIdentifier
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.core.utils.image import shift_img
from tomwer.io.utils import get_slice_data
from tomwer.gui.qfolderdialog import QScanDialog
from tomwer.gui.reconstruction.axis.CompareImages import CompareImages as _CompareImages
from tomwer.gui.visualization.diffviewer.shiftwidget import TwoFramesShiftTab
from silx.gui import qt
from silx.io.url import DataUrl
from silx.utils.enum import Enum as _Enum

_logger = logging.getLogger(__name__)


class CompareImages(_CompareImages):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # ignore Pan with arrow keys. This should be used by the "arrowControlWidget"
        self.getPlot().setPanWithArrowKeys(False)
        self._firstVisible = True

    def setVisible(self, bool):
        if self._firstVisible:
            # hack to enforce matplotlib to replot the widget.
            # because it looks like it is missing to find the correct viewport
            # when not visible
            self.getPlot().resetZoom()
            self._firstVisible = False
        super().setVisible(bool)


class _FrameSelector(qt.QWidget):
    """Selector to select a frame from dark, flat, projection (normalized or
    not) and a reconstruction"""

    sigCorrectionChanged = qt.Signal()
    """signal emitted when the correction changed"""
    sigSelectedUrlChanged = qt.Signal()
    """signal emitted when the selected url changed"""

    class FrameType(_Enum):
        DARKS = "darks"
        FLATS = "flats"
        PROJ = "projections"
        ALIGN_PROJ = "alignment projections"
        RECON_SLICES = "slices reconstructed"

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self._scan = None

        self.setLayout(qt.QFormLayout())
        self._frameTypeCB = qt.QComboBox(self)
        for frame_type in _FrameSelector.FrameType:
            self._frameTypeCB.addItem(frame_type.value)
        self.layout().addRow("frame type", self._frameTypeCB)
        self._frameUrlCB = qt.QComboBox(self)
        self.layout().addRow("frame", self._frameUrlCB)
        self._proj_normalized = qt.QCheckBox("corrected", self)
        self.layout().addRow("", self._proj_normalized)

        # connect signal / slot
        self._frameTypeCB.currentIndexChanged.connect(self._typeChanged)
        self._frameUrlCB.currentIndexChanged.connect(self._urlChanged)
        self._proj_normalized.toggled.connect(self._correctionChanged)

        # default settings
        self._proj_normalized.setChecked(True)
        index = self._frameTypeCB.findText(self.FrameType.PROJ.value)
        self._frameTypeCB.setCurrentIndex(index)

    def setScan(self, scan):
        self._scan = scan
        self._typeChanged()

    def getScan(self):
        return self._scan

    def getCurrentUrl(self):
        if self._frameUrlCB.currentText() != "":
            return DataUrl(path=self._frameUrlCB.currentData(qt.Qt.UserRole))
        else:
            return None

    def getTypeSelected(self):
        return self.FrameType.from_value(self._frameTypeCB.currentText())

    def _typeChanged(self, *args, **kwargs):
        type_selected = self.FrameType.from_value(self.getTypeSelected())
        self._proj_normalized.setVisible(
            type_selected in (self.FrameType.PROJ, self.FrameType.ALIGN_PROJ)
        )
        if self._scan is None:
            return

        urls = []
        self._frameUrlCB.clear()
        if type_selected == self.FrameType.DARKS:
            if self._scan.darks is not None:
                urls = self._scan.darks.values()
        elif type_selected == self.FrameType.FLATS:
            if self._scan.flats is not None:
                urls = self._scan.flats.values()
        elif type_selected == self.FrameType.PROJ:
            if self._scan.projections is not None:
                urls = self._scan.projections.values()
        elif type_selected == self.FrameType.ALIGN_PROJ:
            if self._scan.alignment_projections is not None:
                urls = self._scan.alignment_projections.values()
        elif type_selected == self.FrameType.RECON_SLICES:
            urls = self._scan.get_reconstructions_urls()
        else:
            raise ValueError("Type {} not managed".format(type_selected))
        urls = sorted(urls, key=lambda url: url.path())
        for url in urls:
            if url.data_slice() is not None:
                text = "?slice=".join(
                    (os.path.basename(url.file_path()), str(url.data_slice()))
                )
            else:
                text = os.path.basename(url.file_path())
            user_data = url.path()
            self._frameUrlCB.addItem(text, user_data)

    def _urlChanged(self, *args, **kwargs):
        self.sigSelectedUrlChanged.emit()

    def _correctionChanged(self, *args, **kwargs):
        self.sigCorrectionChanged.emit()

    def needToNormalize(self):
        """

        :return: True if the data need to be treated by a dark and flat field
                 normalization.
        """
        return self._proj_normalized.isChecked() and self.getTypeSelected() in (
            self.FrameType.PROJ,
            self.FrameType.ALIGN_PROJ,
        )

    def clear(self):
        self._scan = None
        self._frameUrlCB.clear()


class _FramesSelector(qt.QWidget):
    """Selector to select a frame from dark, flat, projection (normalized or
    not) and a reconstruction"""

    sigLeftFrameUpdateReq = qt.Signal()
    """signal emit when a left frame update is requested"""
    sigRightFrameUpdateReq = qt.Signal()
    """signal emit when a right frame update is requested"""

    sigLeftScanChanged = qt.Signal()
    """signal emit when the scan for the left display changed"""
    sigRightScanChanged = qt.Signal()
    """signal emit when the scan for the right display changed"""

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        self._leftScanCB = _ScanComboBox(self)
        self.layout().addWidget(self._leftScanCB, 0, 0, 1, 4)
        self._rightScanCB = _ScanComboBox(self)
        self.layout().addWidget(self._rightScanCB, 0, 4, 1, 4)

        self._leftSelector = _FrameSelector(parent=self)
        self.layout().addWidget(self._leftSelector, 1, 0, 3, 4)
        self._rightSelector = _FrameSelector(parent=self)
        self.layout().addWidget(self._rightSelector, 1, 4, 3, 4)

        # signal / slot connection
        self._leftSelector.sigCorrectionChanged.connect(self._leftFrameUpdReq)
        self._rightSelector.sigCorrectionChanged.connect(self._rightFrameUpdReq)
        self._leftSelector.sigSelectedUrlChanged.connect(self._leftFrameUpdReq)
        self._rightSelector.sigSelectedUrlChanged.connect(self._rightFrameUpdReq)
        self._leftScanCB.sigScanChanged.connect(self._leftScanChanged)
        self._rightScanCB.sigScanChanged.connect(self._rightScanChanged)
        self._leftScanCB.sigRequestScanAdd.connect(self._addScanFrmDialogLeft)
        self._rightScanCB.sigRequestScanAdd.connect(self._addScanFrmDialogRight)

    def getLeftScan(self):
        return self._leftSelector.getScan()

    def setLeftScan(self, scan):
        self._leftScanCB.setScan(scan.get_dataset_identifier())
        self._leftSelector.setScan(scan)

    def getRightScan(self):
        return self._rightSelector.getScan()

    def setRightScan(self, scan):
        self._rightScanCB.setScan(scan.get_dataset_identifier())
        self._rightSelector.setScan(scan)

    def addScan(self, scan):
        if not isinstance(scan, TomwerScanBase):
            raise TypeError("scan should be an instance of {}".format(TomwerScanBase))
        self._leftScanCB.addScan(scan.get_dataset_identifier())
        self._rightScanCB.addScan(scan.get_dataset_identifier())

    def _leftScanChanged(self):
        self._leftSelector.setScan(self._leftScanCB.getCurrentScan())

    def _rightScanChanged(self):
        self._rightSelector.setScan(self._rightScanCB.getCurrentScan())

    def getLeftUrl(self):
        return self._leftSelector.getCurrentUrl()

    def needToNormalizeLeft(self):
        return self._leftSelector.needToNormalize()

    def needToNormalizeRight(self):
        return self._rightSelector.needToNormalize()

    def getRightUrl(self):
        return self._rightSelector.getCurrentUrl()

    def _rightFrameUpdReq(self):
        self.sigRightFrameUpdateReq.emit()

    def _leftFrameUpdReq(self):
        self.sigLeftFrameUpdateReq.emit()

    def _addScanFrmDialogLeft(self):
        self._addScanFrmDialog(link_to="left")

    def _addScanFrmDialogRight(self):
        self._addScanFrmDialog(link_to="right")

    def _addScanFrmDialog(self, link_to: str):
        assert link_to in ("left", "right"), "add scan should be in " "'left', 'right'"

        dialog = QScanDialog(self, multiSelection=True)

        if not dialog.exec_():
            dialog.close()
            return

        foldersSelected = dialog.files_selected()
        scan_to_set = None
        for folder in foldersSelected:
            try:
                scans = ScanFactory.create_scan_objects(scan_path=folder)
            except Exception as e:
                _logger.error(
                    "cannot create scan instances from {}. Error is {}".format(
                        folder, e
                    )
                )
            else:
                for scan in scans:
                    self._leftScanCB.addScan(scan.get_dataset_identifier())
                    self._rightScanCB.addScan(scan.get_dataset_identifier())
                    scan_to_set = scan

        if scan_to_set is not None:
            if link_to == "left":
                self._leftScanCB.setScan(scan_id=scan_to_set.get_dataset_identifier())
            else:
                self._rightScanCB.setScan(scan_id=scan_to_set.get_dataset_identifier())

    def clear(self):
        self._leftScanCB.clear()
        self._rightScanCB.clear()
        self._leftSelector.clear()
        self._rightSelector.clear()


class DiffFrameViewer(qt.QMainWindow):
    """
    Widget used to compare two frames using the silx CompareImages widget.

    User can select a reconstruction, a projection (normalized or not), flat
    or dark.
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        # add frame selector
        self._framesSelector = _FramesSelector(parent=self)
        self._framesSelector.setContentsMargins(0, 0, 0, 0)
        self._framesSelector.layout().setContentsMargins(0, 0, 0, 0)
        self._framesSelectorDW = qt.QDockWidget(parent=self)
        self._framesSelectorDW.setWidget(self._framesSelector)
        self._framesSelectorDW.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.TopDockWidgetArea, self._framesSelectorDW)

        # add shift dock widget
        self._shiftsWidget = TwoFramesShiftTab(self)
        self._shiftsWidget.setContentsMargins(2, 2, 2, 2)

        self._shiftDW = qt.QDockWidget(parent=self)
        self._shiftDW.setWidget(self._shiftsWidget)
        self._shiftDW.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.BottomDockWidgetArea, self._shiftDW)

        # define central widget
        self._mainWidget = CompareImages(parent=self)
        self._mainWidget.setVisualizationMode(
            CompareImages.VisualizationMode.COMPOSITE_A_MINUS_B
        )

        self.setCentralWidget(self._mainWidget)

        # toolbar
        # add toolbar
        toolbar = qt.QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        # add filtering
        style = qt.QApplication.instance().style()
        icon = style.standardIcon(qt.QStyle.SP_DialogResetButton)
        self._clearAction = qt.QAction(icon, "Clear", toolbar)
        toolbar.addAction(self._clearAction)
        self._clearAction.triggered.connect(self.clear)

        # set up
        self._mainWidget.setAutoResetZoom(False)
        self._shiftsWidget.setFocus(qt.Qt.OtherFocusReason)

        # connect signal / slot
        self._framesSelector.sigRightFrameUpdateReq.connect(self._resetRightFrame)
        self._framesSelector.sigLeftFrameUpdateReq.connect(self._resetLeftFrame)
        self._shiftsWidget.sigShiftsChanged.connect(self._frameShiftsChanged)

    def getShiftsWidget(self):
        return self._shiftsWidget

    def addScan(self, scan):
        self._framesSelector.addScan(scan=scan)

    def getLeftScan(self) -> TomwerScanBase:
        return self._framesSelector.getLeftScan()

    def setLeftScan(self, scan: TomwerScanBase):
        return self._framesSelector.setLeftScan(scan)

    def getRightScan(self) -> TomwerScanBase:
        return self._framesSelector.getRightScan()

    def setRightScan(self, scan: TomwerScanBase):
        return self._framesSelector.setRightScan(scan)

    def getShiftFrameA(self) -> tuple:
        return self._shiftsWidget.getFrameAShift()

    def getShiftFrameB(self) -> tuple:
        return self._shiftsWidget.getFrameBShift()

    def isFrameALRFlip(self) -> bool:
        return self._shiftsWidget.isFrameALRFlip()

    def isFrameBLRFlip(self) -> bool:
        return self._shiftsWidget.isFrameBLRFlip()

    def _resetLeftFrame(self):
        scan = self.getLeftScan()
        if scan is None:
            return
        url = self._framesSelector.getLeftUrl()
        if url is None:
            return
        assert isinstance(url, DataUrl)
        data = self._get_data(url.path())
        if self._framesSelector.needToNormalizeLeft():
            data = scan.data_flat_field_correction(
                data=data, index=scan.get_url_proj_index(url)
            )
        if data.ndim != 2:
            if data.ndim == 3 and data.shape[0] == 1:
                data = data.reshape((data.shape[1], data.shape[2]))
            else:
                _logger.error("Cannot display {}. Should be 2D".format(url.path()))
                return

        if self.isFrameALRFlip():
            data = numpy.fliplr(data)
        shifted_image = shift_img(
            data=data, dx=self.getShiftFrameA()[0], dy=self.getShiftFrameA()[1]
        )
        self._mainWidget.setImage1(shifted_image)

    @functools.lru_cache(maxsize=4)
    def _get_data(self, url: str):
        if not isinstance(url, str):
            raise TypeError(f"url should be a str not {type(url)}")
        return get_slice_data(DataUrl(path=url))

    def _resetRightFrame(self):
        scan = self.getRightScan()
        if scan is None:
            return
        url = self._framesSelector.getRightUrl()
        if url is None:
            return
        assert isinstance(url, DataUrl)
        data = self._get_data(url.path())
        if self._framesSelector.needToNormalizeRight():
            data = scan.data_flat_field_correction(
                data=data, index=scan.get_url_proj_index(url)
            )
        if data.ndim != 2:
            if data.ndim == 3 and data.shape[0] == 1:
                data = data.reshape((data.shape[1], data.shape[2]))
            else:
                _logger.error("Cannot display {}. Should be 2D".format(url.path()))
                return
        if self.isFrameBLRFlip():
            data = numpy.fliplr(data)
        shifted_image = shift_img(
            data=data, dx=self.getShiftFrameB()[0], dy=self.getShiftFrameB()[1]
        )
        self._mainWidget.setImage2(shifted_image)

    def clear(self):
        self._framesSelector.clear()
        self._mainWidget.getPlot().clear()

    def _frameShiftsChanged(self):
        self._resetLeftFrame()
        self._resetRightFrame()


class _ScanComboBox(qt.QWidget):
    sigScanChanged = qt.Signal()
    """Signal emit when the scan change"""

    sigRequestScanAdd = qt.Signal()
    """Signal emit when the user request to add a scan from a dialog"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self._scans = set()
        self.setLayout(qt.QHBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        # scan combobox
        self._scansCB = qt.QComboBox(self)
        self.layout().addWidget(self._scansCB)
        # add scan button
        self._addButton = qt.QPushButton(self)
        self._addButton.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self._addButton.setMaximumSize(25, 25)
        # self._addButton.setFixedSize(30, 30)
        style = qt.QApplication.instance().style()
        icon = style.standardIcon(qt.QStyle.SP_DirIcon)
        self._addButton.setIcon(icon)
        self.layout().addWidget(self._addButton)

        # connect signal / slot
        self._scansCB.currentIndexChanged.connect(self._scanChanged)
        self._addButton.pressed.connect(self._addScanCallback)

    def clear(self):
        self._scans = set()
        self._scansCB.clear()

    def addScan(self, scan_id: DatasetIdentifier):
        if not isinstance(scan_id, DatasetIdentifier):
            raise TypeError("scan should be the scan identifier")
        if scan_id not in self._scans:
            self._scans.add(scan_id)
            self._scansCB.addItem(str(scan_id), scan_id)

    def setScan(self, scan_id: DatasetIdentifier):
        if not isinstance(scan_id, DatasetIdentifier):
            raise TypeError("scan should be the scan identifier")
        idx = self._scansCB.findText(str(scan_id))
        self._scansCB.setCurrentIndex(idx)

    def _scanChanged(self, *args, **kwargs):
        self.sigScanChanged.emit()

    def getCurrentScan(self) -> TomwerScanBase:
        current_idx = self._scansCB.currentIndex()
        dataset_id = self._scansCB.itemData(current_idx)
        try:
            scan = DatasetIdentifier.recreate_dataset(dataset_id)
        except Exception as e:
            _logger.error(
                "Fail to recreate dataset from {}. Reason is {}."
                "".format(str(dataset_id), e)
            )
            return None
        else:
            return scan

    def _addScanCallback(self):
        self.sigRequestScanAdd.emit()
