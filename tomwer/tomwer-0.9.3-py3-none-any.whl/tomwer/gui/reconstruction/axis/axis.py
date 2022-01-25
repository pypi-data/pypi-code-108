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
contains gui relative to axis calculation using sinogram
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "14/10/2019"


from silx.gui import qt

from tomwer.core.scan.scanbase import TomwerScanBase
from .radioaxis import RadioAxisWindow
from ...utils.scandescription import ScanNameLabel
from tomwer.core.process.reconstruction.axis.mode import AxisMode
from tomwer.gui.utils.buttons import PadlockButton
from tomwer.synctools.axis import QAxisRP
from silx.utils.deprecation import deprecated
import logging

_logger = logging.getLogger(__file__)


class _AxisTypeSelection(qt.QGroupBox):
    sigSelectionChanged = qt.Signal(str)
    """Signal emitted when the selection changed. Value can be `sinogram` or
    `radio`"""

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent=parent)
        self.setTitle("compute center of rotation from")
        self.setLayout(qt.QHBoxLayout())
        self._radioRB = qt.QRadioButton("radios", parent=self)
        self.layout().addWidget(self._radioRB)

        self._sinogramRB = qt.QRadioButton("sinogram", parent=self)
        self.layout().addWidget(self._sinogramRB)

        # Signal / Slot connections
        self._radioRB.toggled.connect(self._selectionChanged)
        self._sinogramRB.toggled.connect(self._selectionChanged)

    def getSelection(self):
        if self._radioRB.isChecked():
            return "radio"
        else:
            return "sinogram"

    def setSelection(self, selection):
        if selection == "radio":
            self._radioRB.setChecked(True)
        elif selection == "sinogram":
            self._sinogramRB.setChecked(True)
        else:
            raise ValueError("invalid selection given")

    def _selectionChanged(self, *args, **kwargs):
        self.sigSelectionChanged.emit(self.getSelection())


class AxisWindow(qt.QMainWindow):
    """Main widget for the axis calculation"""

    sigComputationRequested = qt.Signal()
    """signal emitted when a computation is requested"""

    sigApply = qt.Signal()
    """signal emitted when the axis reconstruction parameters are validated"""

    sigAxisEditionLocked = qt.Signal(bool)
    """Signal emitted when the status of the reconstruction parameters edition
    change"""

    sigLockModeChanged = qt.Signal()
    """Signal emitted when the lock on the method change"""

    def __init__(self, axis_params, parent=None):
        qt.QMainWindow.__init__(self, parent=parent)
        self._mainWidget = qt.QWidget(self)
        self._mainWidget.setLayout(qt.QVBoxLayout())
        self.setCentralWidget(self._mainWidget)

        self._axis_params = axis_params

        # add scan name
        self._scan_label = ScanNameLabel(parent=self)
        self._mainWidget.layout().addWidget(self._scan_label)

        # add selection
        self._selectionGB = _AxisTypeSelection(parent=self)
        self._mainWidget.layout().addWidget(self._selectionGB)
        self._selectionGB.hide()

        # add widget for radio and sinogram axis
        self._axisWidget = _AxisWidget(parent=self, axis_params=axis_params)
        self._mainWidget.layout().addWidget(self._axisWidget)

        self.setCentralWidget(self._mainWidget)

        # set up configuration
        if axis_params.use_sinogram:
            selection = "sinogram"
        else:
            selection = "radio"
        self._selectionGB.setSelection(selection=selection)
        self._selectionGB._selectionChanged(self._selectionGB.getSelection())

        # connect signal / slots
        self._axisWidget.sigValidateRequest.connect(self._repeatValidateRequest)
        self._axisWidget.sigComputationRequested.connect(self._computationRequested)
        self._axisWidget.sigLockModeChanged.connect(self._lockModeChanged)
        self._selectionGB.sigSelectionChanged.connect(self._axisWidget._axisTypeChanged)
        self._axisWidget.sigSinogramReady.connect(self._computationReady)

        # expose API
        self.setSelection = self._selectionGB.setSelection
        self.getSelection = self._selectionGB.getSelection
        self.hideLockButton = self._axisWidget.hideLockButton
        self.hideApplyButton = self._axisWidget.hideApplyButton
        self.setReconsParams = self._axisWidget.setReconsParams
        self.getPlotWidget = self._axisWidget.getPlotWidget
        self.setMode = self._axisWidget.setMode
        self.manual_uses_full_image = self._axisWidget.manual_uses_full_image
        self.setModeLock = self._axisWidget.setModeLock
        self.getAxis = self._axisWidget.getAxis
        self.isModeLock = self._axisWidget.isModeLock
        self.isValueLock = self._axisWidget.isValueLock
        self.setValueLock = self._axisWidget.setValueLock
        self._setValueLockFrmSettings = self._axisWidget._setValueLockFrmSettings
        self._setModeLockFrmSettings = self._axisWidget._setModeLockFrmSettings
        self.getRadioMode = self._axisWidget.getRadioMode
        self.getEstimatedCor = self._axisWidget.getEstimatedCor
        self.sigMethodChanged = self._axisWidget.sigModeChanged

    def _disableForProcessing(self, *args, **kwargs):
        self._mainWidget.setEnabled(False)
        self._axisWidget.setEnabled(False)

    def _enableForProcessing(self, *args, **kwargs):
        self._mainWidget.setEnabled(True)
        self._axisWidget.setEnabled(True)

    def _lockModeChanged(self):
        self.sigLockModeChanged.emit()

    def setScan(self, scan, set_position=True):
        """
        set the gui for this scan

        :param TomoBase scan:
        """
        self._scan_label.setScan(scan=scan)
        self._axisWidget.setScan(scan=scan, set_position=set_position)
        self._enableSinogramOpt(scan.scan_range == 360)

    def _enableSinogramOpt(self, b):
        if self._selectionGB.getSelection() == "sinogram" and not b:
            change_selection_to_radio = True
        else:
            change_selection_to_radio = False
        self._selectionGB._sinogramRB.setEnabled(b)
        if change_selection_to_radio:
            self._selectionGB.setSelection("radio")

    def _computationRequested(self):
        self._computationReady()

    def _computationReady(self):
        self.sigComputationRequested.emit()

    def _repeatValidateRequest(self):
        self.sigApply.emit()

    def setPosition(self, frm: float, value: float):
        self._axisWidget.setPosition(value_ref_tomwer=value)


class _AxisWidget(qt.QMainWindow):
    """
    Control which plot and which settings widget is displayed
    """

    sigComputationRequested = qt.Signal()

    sigValidateRequest = qt.Signal()

    sigLockCORValueChanged = qt.Signal(bool)
    """bool: True if locked"""

    sigLockModeChanged = qt.Signal()
    """Signal emitted when the lock mode on the mode change"""

    sigModeChanged = qt.Signal(str)

    sigSinogramReady = qt.Signal()

    def __init__(self, parent, axis_params):
        qt.QMainWindow.__init__(self, parent)
        self._settingsWidget = None
        self.setDockOptions(qt.QMainWindow.AnimatedDocks)

        self._settingsDockWidget = qt.QDockWidget(parent=self)
        self._settingsDockWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._settingsDockWidget)

        self._controlWidget = _ControlWidget(parent=self)
        self._controlWidget.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        self._controlDockWidget = qt.QDockWidget(parent=self)
        self._controlDockWidget.setWidget(self._controlWidget)
        self._controlDockWidget.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._controlDockWidget)

        self._axis_params = axis_params
        self._radioAxis = RadioAxisWindow(parent=self, axis=axis_params)
        self._plotWidgets = qt.QWidget(self)
        self._plotWidgets.setLayout(qt.QVBoxLayout())
        self.setCentralWidget(self._plotWidgets)

        # expose API
        self.getRadioMode = self._radioAxis.getMode
        self.getEstimatedCor = self._radioAxis.getEstimatedCor

        # set up
        if self._axis_params.mode is AxisMode.manual:
            self._controlWidget.setPosition(
                self._axis_params.relative_cor_value,
                self._axis_params.absolute_cor_value,
            )

        # connect signal / slots
        self._controlWidget.sigComputationRequest.connect(
            self._repeatComputationRequest
        )
        self._controlWidget.sigValidateRequest.connect(self._repeatValidateRequest)
        self._controlWidget.sigLockCORValueChanged.connect(self._CORValueLocked)
        self._radioAxis.sigLockModeChanged.connect(self._lockModeChanged)
        self._radioAxis.sigPositionChanged.connect(self._setPositionFrmTuple)

        # set up
        self.addPlot(self._radioAxis)
        self.setActiveWidget(self._radioAxis)

    @deprecated(replacement="getRadioMode")
    def getMode(self):
        return self._radioAxis.getMode()

    def _sinoAxisReady(self):
        self.sigSinogramReady.emit()

    def manual_uses_full_image(self, value):
        self._radioAxis.manual_uses_full_image(value)

    def _modeChanged(self):
        self.getAxis().mode = self.getMode()
        self.getAxis().use_sinogram = self.useSinogram()

    def _lockModeChanged(self):
        self.sigLockModeChanged.emit()

    def _repeatComputationRequest(self):
        self.sigComputationRequested.emit()

    def _repeatValidateRequest(self):
        self.sigValidateRequest.emit()

    def setMode(self, mode):
        mode = AxisMode.from_value(mode)
        self.setActiveWidget(self._radioAxis)
        self._radioAxis.setMode(mode)
        self._axis_params.mode = mode
        self.sigModeChanged.emit(mode.value)

    def _CORValueLocked(self, lock):
        if lock:
            self.setMode(AxisMode.manual)
        self.setModeLock(lock)
        self.sigLockCORValueChanged.emit(lock)

    def setActiveWidget(self, widget):
        for iPlotWidget in range(self._plotWidgets.layout().count()):
            plotWidget = self._plotWidgets.layout().itemAt(iPlotWidget).widget()
            plotWidget.setVisible(widget == plotWidget)
        self.setSettingsWidget(widget.getSettingsWidget())

    def addPlot(self, plot):
        self._plotWidgets.layout().addWidget(plot)

    def setPlotWidget(self, plot):
        self.setCentralWidget(plot)

    def getPlotWidget(self):
        return self.centralWidget()

    def setSettingsWidget(self, widget):
        self._settingsDockWidget.setWidget(widget)

    def _setPositionFrmTuple(self, value):
        self.setPosition(value_ref_tomwer=value[0])

    def setPosition(
        self, value_ref_tomwer: float, value_ref_nabu: float = None
    ) -> None:
        """

        :param float value_ref_tomwer: center of rotation value on tomwer
                                       reference
        :param float value_ref_nabu: center of rotation value on the nabu
                                     reference
        :raises: ValueError if the frm parameter is not recognized
        """
        if (
            value_ref_nabu is None
            and self._axis_params.frame_width is not None
            and value_ref_tomwer is not None
        ):
            try:
                value_ref_nabu = value_ref_tomwer + self._axis_params.frame_width / 2.0
            except TypeError:
                value_ref_nabu = None
        self._controlWidget.setPosition(
            value_ref_tomwer=value_ref_tomwer, value_ref_nabu=value_ref_nabu
        )
        if value_ref_tomwer is not None:
            self._radioAxis.setXShift(value_ref_tomwer)
        else:
            self._radioAxis.resetShift()

    def getAxis(self):
        return self._axis_params

    def _axisTypeChanged(self, selection):
        self._axis_params.use_sinogram = False
        self.setActiveWidget(self._radioAxis)

    def setScan(self, scan: TomwerScanBase, set_position):
        """
        set the gui for this scan

        :param TomoBase scan:
        """
        self._radioAxis.setScan(scan=scan)
        if set_position is True and scan.axis_params is not None:
            self.setPosition(
                scan.axis_params.relative_cor_value, scan.axis_params.relative_cor_value
            )
        elif set_position is False:
            if scan.dim_1 is not None:
                self._controlWidget._updateAbsolutePosition(width=scan.dim_1)

    def _applyRequested(self) -> None:
        self.sigApply.emit()

    def _computationRequested(self) -> None:
        self.sigComputationRequested.emit()

    def hideLockButton(self) -> None:
        self._controlWidget.hideLockButton()

    def hideApplyButton(self) -> None:
        self._controlWidget.hideApplyButton()

    def _setModeLockFrmSettings(self, lock):
        old = self.blockSignals(True)
        self._radioAxis._setModeLockFrmSettings(lock)
        self.blockSignals(old)

    def _setValueLockFrmSettings(self, lock):
        old = self.blockSignals(True)
        self.setValueLock(lock)
        self.blockSignals(old)

    def setModeLock(self, lock):
        assert type(lock) is bool
        self._radioAxis.setLocked(lock)

    def isModeLock(self):
        return self._radioAxis.isModeLock()

    def isValueLock(self):
        return self._controlWidget.isValueLock()

    def setValueLock(self, lock):
        self._controlWidget.setValueLock(lock)

    def setReconsParams(self, recons_params):
        self._axis_params = recons_params
        self._radioAxis.setReconsParams(axis=recons_params)
        if recons_params.mode is AxisMode.manual:
            self._controlWidget.setPosition(
                self._axis_params.relative_cor_value,
                self._axis_params.absolute_cor_value,
            )


class _ControlWidget(qt.QWidget):
    """
    Widget to lock cor position or compute it or validate it and to
    display the cor value
    """

    sigComputationRequest = qt.Signal()
    """Signal emitted when user request a computation from the settings"""

    sigValidateRequest = qt.Signal()
    """Signal emitted when user validate the current settings"""

    sigLockCORValueChanged = qt.Signal(bool)
    """Signal emitted when the user lock the cor value. Param: True if lock"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        # display 'center' information
        self._positionInfo = _PositionInfoWidget(parent=self)
        self.layout().addWidget(self._positionInfo)

        self._buttons = qt.QWidget(parent=self)
        self._buttons.setLayout(qt.QHBoxLayout())
        self.layout().addWidget(self._buttons)

        self._lockBut = PadlockButton(parent=self)
        self._lockBut.setAutoDefault(False)
        self._lockBut.setDefault(False)

        self._buttons.layout().addWidget(self._lockBut)
        self._lockLabel = qt.QLabel("lock cor value", parent=self)
        self._buttons.layout().addWidget(self._lockLabel)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self._buttons.layout().addWidget(spacer)

        self._computeBut = qt.QPushButton("compute", parent=self)
        self._buttons.layout().addWidget(self._computeBut)
        style = qt.QApplication.style()
        applyIcon = style.standardIcon(qt.QStyle.SP_DialogApplyButton)
        self._applyBut = qt.QPushButton(applyIcon, "validate", parent=self)
        self._buttons.layout().addWidget(self._applyBut)
        self.layout().addWidget(self._buttons)

        # set up
        self._positionInfo.setPosition(None, None)

        # make connection
        self._computeBut.pressed.connect(self._needComputation)
        self._applyBut.pressed.connect(self._validate)
        self._lockBut.sigLockChanged.connect(self._lockValueChanged)

    def hideLockButton(self) -> None:
        self._lockLabel.hide()
        self._lockBut.hide()

    def hideApplyButton(self) -> None:
        self._applyBut.hide()

    def _lockValueChanged(self):
        self.sigLockCORValueChanged.emit(self._lockBut.isLocked())
        self._computeBut.setEnabled(not self._lockBut.isLocked())

    def _needComputation(self, *arg, **kwargs):
        """callback when the radio line changed"""
        self.sigComputationRequest.emit()

    def _validate(self):
        self.sigValidateRequest.emit()

    def setPosition(self, value_ref_tomwer, value_ref_nabu):
        self._positionInfo.setPosition(
            value_ref_tomwer=value_ref_tomwer, value_ref_nabu=value_ref_nabu
        )

    def _updateAbsolutePosition(self, width):
        self._positionInfo._updateAbsolutePosition(width=width)

    def isValueLock(self):
        return self._lockBut.isLocked()

    def setValueLock(self, lock):
        self._lockBut.setLock(lock)


class _PositionInfoWidget(qt.QWidget):
    """Widget used to display information relative to the current position"""

    def __init__(self, parent, axis=None):
        self._axis = None
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())
        centerLabel = qt.QLabel("center", parent=self)
        centerLabel.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        font = centerLabel.font()
        font.setBold(True)
        centerLabel.setFont(font)

        self.layout().addWidget(centerLabel, 0, 0, 1, 1)
        self.layout().addWidget(qt.QLabel(" (relative):"), 0, 1, 1, 1)

        self._tomwerPositionLabel = qt.QLineEdit("", parent=self)
        self._tomwerPositionLabel.setReadOnly(True)
        self._tomwerPositionLabel.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )
        self._tomwerPositionLabel.setStyleSheet("color: red")
        self.layout().addWidget(self._tomwerPositionLabel, 0, 2, 1, 1)

        centerLabel = qt.QLabel("center", parent=self)
        centerLabel.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        font = centerLabel.font()
        font.setBold(False)
        centerLabel.setFont(font)

        self.layout().addWidget(centerLabel, 1, 0, 1, 1)
        self.layout().addWidget(qt.QLabel(" (absolute):"), 1, 1, 1, 1)
        self._nabuPositionLabel = qt.QLineEdit("", parent=self)
        self._nabuPositionLabel.setReadOnly(True)
        self._nabuPositionLabel.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )
        self._nabuPositionLabel.setStyleSheet("color: #ff8c00")
        self.layout().addWidget(self._nabuPositionLabel, 1, 2, 1, 1)

        if axis:
            self.setAxis(axis)

    def setAxis(self, axis):
        assert isinstance(axis, QAxisRP)
        if axis == self._axis:
            return
        if self._axis is not None:
            self._axis.sigChanged.disconnect(self._updatePosition)
        self._axis = axis
        self._axis.sigChanged.connect(self._updatePosition)
        self._updatePosition()

    def _updatePosition(self):
        if self._axis:
            if self._axis.relative_cor_value is None:
                value = "?"
                self._tomwerPositionLabel.setText(value)
                self._nabuPositionLabel.setText(value)
            else:
                self._tomwerPositionLabel.setText(str(self._axis.relative_cor_value))
                self._nabuPositionLabel.setText(str(self._axis.value_ref_nabu))

    def getPosition(self):
        return float(self._tomwerPositionLabel.text())

    def setPosition(self, value_ref_tomwer, value_ref_nabu):
        if value_ref_tomwer is None:
            self._tomwerPositionLabel.setText("?")
        else:
            self._tomwerPositionLabel.setText(str(value_ref_tomwer))
        if value_ref_nabu is None:
            self._nabuPositionLabel.setText("?")
        else:
            self._nabuPositionLabel.setText(str(value_ref_nabu))

    def _updateAbsolutePosition(self, width):
        rel_value = self._tomwerPositionLabel.text()
        if rel_value.isnumeric() and width is not None:
            abs_value = float(rel_value) + width / 2.0
            self._nabuPositionLabel.setText(str(abs_value))
