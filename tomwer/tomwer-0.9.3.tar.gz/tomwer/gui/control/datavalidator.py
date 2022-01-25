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
__date__ = "23/07/2020"


from silx.gui import qt
from tomwer.gui.visualization.dataviewer import DataViewer
from tomwer.core.process.control.scanvalidator import ScanValidator as BaseDataValidator
from tomwer.gui.utils.waiterthread import QWaiterThread
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.core.scan.scanbase import _TomwerBaseDock
from tomwer.gui.qfolderdialog import QScanDialog
from tomwer.core.scan.scanfactory import ScanFactory
import weakref
from contextlib import AbstractContextManager
import logging
import time

_logger = logging.getLogger(__file__)


WAIT_TIME_MEM_REL = 20
"""Time (in sec) to wait to check if the scan validator has to release his
stack of scans. This is a security to make sure we are not keeping
unnecessary data during an acquisition in lbsram"""


class DataValidator(qt.QMainWindow, BaseDataValidator):
    """
    Widget used to validate an acquisition or recall some processing
    """

    sigScanReady = qt.Signal(TomwerScanBase)
    """signal emitted when a scan is validated"""

    sigChangeReconsParams = qt.Signal(_TomwerBaseDock)
    """signal emitted when the user request modifications on reconstruction
    parameters"""

    class SliderCM(AbstractContextManager):
        """Simple context manager to hida / show button dialogs"""

        def __init__(self, slider):
            self._slider = slider
            self._old = None

        def __enter__(self):
            self._old = self._slider.blockSignals(True)

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._slider.blockSignals(self._old)

    def __init__(self, parent, timeout_loop_memory=WAIT_TIME_MEM_REL):
        qt.QMainWindow.__init__(
            self, parent, memoryReleaser=QWaiterThread(timeout_loop_memory)
        )
        # needed on lbs191... otherwise crash with PyQt5.11. with a QThread destroyed...
        time.sleep(0.01)
        BaseDataValidator.__init__(
            self, memoryReleaser=QWaiterThread(timeout_loop_memory)
        )
        self._centralWidget = DataViewer(parent=parent)
        self.setCentralWidget(self._centralWidget)

        # scan slider and add scan
        self._lateralWidget = qt.QWidget(self)
        self._lateralWidget.setLayout(qt.QVBoxLayout())
        self._addScanButton = qt.QPushButton(self)
        style = qt.QApplication.style()
        icon = style.standardIcon(qt.QStyle.SP_DirIcon)
        self._addScanButton.setIcon(icon)
        self._lateralWidget.layout().addWidget(self._addScanButton)
        self._scanSelectorSlider = _ScanSelectorWidget(parent=self)
        self._lateralWidget.layout().addWidget(self._scanSelectorSlider)
        self._lateralWidget.layout().setContentsMargins(0, 0, 0, 0)

        self._scanSelectorSliderDocker = qt.QDockWidget(self)
        self._scanSelectorSliderDocker.setWidget(self._lateralWidget)
        self._scanSelectorSliderDocker.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._scanSelectorSliderDocker)

        # control buttons
        self._controlButtons = _DataControlWidget(parent=self)
        self._controlButtonsDocker = qt.QDockWidget(self)
        self._controlButtonsDocker.setWidget(self._controlButtons)
        self._controlButtonsDocker.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.BottomDockWidgetArea, self._controlButtonsDocker)

        self._scanSelectorSlider.setMinimum(0)
        self._scanSelectorSlider.setMaximum(0)

        # connect signal / slot
        self._scanSelectorSlider.sigScanChanged.connect(self._updateCurrentScan)
        _controlButtons = self._controlButtons
        _controlButtons.sigValidateScan.connect(self.validateCurrentScan)
        _controlButtons.sigChangeReconstructionParametersScan.connect(
            self.changeReconsParamCurrentScan
        )
        _controlButtons.toggled.connect(self.setManualValidation)
        self._addScanButton.pressed.connect(self._addNewScanCallback)

    def close(self) -> bool:
        self._centralWidget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._centralWidget.close()
        self._centralWidget = None
        qt.QMainWindow.close(self)

    def addScan(self, scan):
        """

        :param scan:
        :return:
        """
        assert isinstance(scan, TomwerScanBase)
        BaseDataValidator.addScan(self, scan)

        with self.SliderCM(self._scanSelectorSlider):
            current_index = self._scanSelectorSlider.value()
            self._scanSelectorSlider.setRange(0, len(self._scansToValidate) - 1)
            self._scanSelectorSlider.setValue(current_index)

        if str(scan) in self._scansToValidate:
            self.setActiveScan(scan)

    def setActiveScan(self, scan: TomwerScanBase):
        """

        :param scan:
        :return:
        """
        if scan is None:
            self.clear()
        elif str(scan) not in self._scansToValidate:
            _logger.warning("scan has not been registered")
        else:
            with self.SliderCM(self._scanSelectorSlider):
                self._centralWidget.setScan(scan)
                self._controlButtons.setScan(scan)
                index = list(self._scansToValidate.keys()).index(str(scan))
                self._scanSelectorSlider.setValue(index)

    def _updateCurrentScan(self):
        with self.SliderCM(self._scanSelectorSlider):
            self.setActiveScan(self.getCurrentScan())

    def getCurrentScan(self) -> TomwerScanBase:
        """

        :return:
        """
        current_scan_index = self._scanSelectorSlider.value()
        if current_scan_index >= len(self._scansToValidate):
            return None
        else:
            scan_id = list(self._scansToValidate.keys())[current_scan_index]
            scan = self._scansToValidate[scan_id]
            assert isinstance(scan, TomwerScanBase)
            return scan

    def validateCurrentScan(self):
        scan = self.getCurrentScan()
        if scan is None:
            return
        else:
            BaseDataValidator._validateScan(self, scan)
            with self.SliderCM(self._scanSelectorSlider):
                current_index = self._scanSelectorSlider.value()
                self._scanSelectorSlider.setRange(0, len(self._scansToValidate) - 1)
                # note: slider force the value to be in [minimum, maximum]
                self._scanSelectorSlider.setValue(current_index)
                self._updateCurrentScan()

    def changeReconsParamCurrentScan(self):
        current_scan = self.getCurrentScan()
        if current_scan:
            assert isinstance(current_scan, TomwerScanBase)
            BaseDataValidator._changeReconsParam(self, current_scan)

    def _sendScanReady(self, scan):
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            self.sigScanReady.emit(scan)

    def _sendUpdateReconsParam(self, scan):
        if scan is not None:
            assert isinstance(scan, _TomwerBaseDock)
            self.sigChangeReconsParams.emit(scan)

    def clear(self):
        try:
            self._centralWidget.clear()
        except AttributeError:
            # if has been removed before calling clear
            pass

    def _validateStack(self, filter_=None):
        BaseDataValidator._validateStack(self, filter_=filter_)
        self._updateCurrentScan()

    def setAutomaticValidation(self, auto):
        self._controlButtons.setChecked(not auto)

    def _addNewScanCallback(self):
        """Callback when we want to add a new scan to the scan validator"""
        dialog = QScanDialog(self, multiSelection=True)

        if not dialog.exec_():
            dialog.close()
            return

        foldersSelected = dialog.files_selected()
        new_active_scan = None
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
                    self.addScan(scan=scan)
                    new_active_scan = scan

        if new_active_scan is not None:
            self.setActiveScan(new_active_scan)


class _ScanSelectorWidget(qt.QWidget):
    """Slider to select the scan we want to 'check'"""

    sigScanChanged = qt.Signal(int)
    """signal emitted when the scan change. Value is the scan index"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())

        self._qslider = qt.QSlider(qt.Qt.Vertical, self)
        self.layout().addWidget(self._qslider)

        self._verticalLabel = _VerticalLabel(
            "stack of received scan", parent=self, revert=True
        )
        self.layout().addWidget(self._verticalLabel)

        # connect signal / slot
        self._qslider.valueChanged.connect(self._valueHasChanged)

    def _valueHasChanged(self, *args, **kwargs):
        self.sigScanChanged.emit(self._qslider.value())

    def value(self):
        return self._qslider.value()

    def setValue(self, value):
        self._qslider.setValue(value)

    def setMinimum(self, p_int):
        self._qslider.setMinimum(p_int)

    def setMaximum(self, p_int):
        self._qslider.setMaximum(p_int)

    def setRange(self, p_int, p_int_1):
        self._qslider.setRange(p_int, p_int_1)


class _DataControlWidget(qt.QGroupBox):
    """Set of buttons to control the curremt scan"""

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

    def __init__(self, parent=None):
        qt.QGroupBox.__init__(self, title="Validate manually", parent=parent)
        self._scan = None
        self.setCheckable(True)
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

    def setScan(self, scan):
        self._scan = weakref.ref(scan)

    def setEnabled(self, b):
        self.validateButton.setEnabled(b)
        self.changeReconsParamButton.setEnabled(b)

    def __validated(self):
        """Callback when the validate button is pushed"""
        self.sigValidateScan.emit("")

    def __redoacquisition(self):
        """Callback when the redo acquisition button is pushed"""
        if self._scan is not None and self._scan() is not None:
            self.sigRedoAcquisitionScan.emit(self._scan())

    def __updateReconstructionParameters(self):
        """Callback when the change reconstruction button is pushed"""
        if self._scan is not None and self._scan() is not None:
            self.sigChangeReconstructionParametersScan.emit(self._scan())


class _VerticalLabel(qt.QLabel):
    """Display vertically the given text"""

    def __init__(self, text, parent=None, revert=False):
        """

        :param text: the legend
        :param parent: the Qt parent if any
        """
        qt.QLabel.__init__(self, text, parent)
        self.revert = revert
        self.setLayout(qt.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, event):
        painter = qt.QPainter(self)
        painter.setFont(self.font())

        painter.translate(0, self.rect().height())
        painter.rotate(90)
        if self.revert:
            newRect = qt.QRect(
                -self.rect().height(),
                -self.rect().width(),
                self.rect().height(),
                self.rect().width(),
            )
        else:
            newRect = self.rect()

        painter.drawText(newRect, qt.Qt.AlignHCenter, self.text())

        fm = qt.QFontMetrics(self.font())
        preferedHeight = fm.width(self.text())
        preferedWidth = fm.height()
        self.setFixedWidth(preferedWidth)
        self.setMinimumHeight(preferedHeight)
