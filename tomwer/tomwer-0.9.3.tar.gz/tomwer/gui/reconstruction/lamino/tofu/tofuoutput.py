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
__date__ = "01/06/2018"


import os
from silx.gui import qt
import logging
from tomwer.core.process.reconstruction.lamino.tofu import (
    SLICE_STACK_TYPE,
    ROTATION_CENTER_TYPE,
    LAMINO_ANGLE_TYPE,
    PSI_ANGLE_TYPE,
)
from tomwer.core.settings import get_lbsram_path
from tomwer.core.utils.char import DELTA_CHAR
from tomwer.gui.reconstruction.lamino.tofu import settings
from tomwer.gui.utils.illustrations import _IllustrationWidget
from .TofuOptionLoader import _TofuOptionLoader, _getterSetter
from .misc import _AngleWidget, _RegionLE, PadlockButton

_logger = logging.getLogger(__name__)


class OutputTofuWidget(_TofuOptionLoader, qt.QWidget):
    """
    Main widgets for the tofu reconstruction
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self._scan_type = "slice stack"
        self.__scanID = None
        self.setLayout(qt.QGridLayout())

        self._controlWidget = qt.QWidget(parent=self)
        self._controlWidget.setLayout(qt.QVBoxLayout())

        self._volumeAngleGrp = VolumeAnglesWidget(parent=self)
        self._stepSizeAndRange = StepGroup(parent=self._controlWidget)

        self._planeDisplay = _IllustrationWidget(parent=self)
        self._planeDisplay.setMinimumSize(qt.QSize(250, 250))
        self._planeDisplay.setSizePolicy(
            qt.QSizePolicy.Preferred, qt.QSizePolicy.Preferred
        )
        self._controlWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._controlWidget.layout().addWidget(self._volumeAngleGrp)
        self._controlWidget.layout().addWidget(self._stepSizeAndRange)
        self._region = RegionGB(parent=self)
        self._controlWidget.layout().addWidget(self._region)

        self._outputWidget = _OutputPathWidget(parent=self)
        self.layout().addWidget(self._outputWidget, 1, 0, 1, 2)

        self.layout().addWidget(self._controlWidget, 0, 0)
        self.layout().addWidget(self._planeDisplay, 0, 1)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 2, 0)

        self._controlWidget.setFixedWidth(500)

        # signal/slot connect
        self._volumeAngleGrp.sigPlaneChanged.connect(self._updateOutput)

        # expose API
        self.getAngles = self._volumeAngleGrp._angles.get
        self.getOutput = self._outputWidget.getOutput
        self.setOutput = self._outputWidget.setOutput
        self.lockOutput = self._outputWidget.lock
        self.forceLbsram = self._outputWidget.forceLbsram
        self.setForceLbsram = self._outputWidget.setForceLbsram
        self.isOutputFolderLocked = self._outputWidget.isLocked
        self.removeTiff = self._outputWidget.removeIfExist
        self.setRemoveTiff = self._outputWidget.setRemoveIfExist
        self.setVolumeAngleX = self._volumeAngleGrp.setVolumeAngleX
        self.setVolumeAngleY = self._volumeAngleGrp.setVolumeAngleY
        self.setVolumeAngleZ = self._volumeAngleGrp.setVolumeAngleZ
        self.getVolumeAngleX = self._volumeAngleGrp.getVolumeAngleX
        self.getVolumeAngleY = self._volumeAngleGrp.getVolumeAngleY
        self.getVolumeAngleZ = self._volumeAngleGrp.getVolumeAngleZ
        self.setRegionSelType = self._stepSizeAndRange.setRegionSelType
        self.setRegion = self._stepSizeAndRange.setRegion
        self.getRegion = self._stepSizeAndRange.getRegion
        self.dryRun = self._outputWidget.dryRun
        self.setHighLimit = self._stepSizeAndRange.setHighLimit
        self.resetHighLimit = self._stepSizeAndRange.resetHighLimit
        self.getZ = self._stepSizeAndRange.getZ
        self.setZ = self._stepSizeAndRange.setZ

        options = {
            "x-region": _getterSetter(
                getter=self._region.getXRegion, setter=self._region.setXRegionFrmStr
            ),
            "y-region": _getterSetter(
                getter=self._region.getYRegion, setter=self._region.setYRegionFrmStr
            ),
            "volume-angle-x": _getterSetter(
                getter=self.getVolumeAngleX, setter=self.setVolumeAngleX
            ),
            "volume-angle-y": _getterSetter(
                getter=self.getVolumeAngleY, setter=self.setVolumeAngleY
            ),
            "volume-angle-z": _getterSetter(
                getter=self.getVolumeAngleZ, setter=self.setVolumeAngleZ
            ),
            "region": _getterSetter(getter=self.getRegion, setter=self.setRegion),
            "output": _getterSetter(getter=self.getOutput, setter=self.setOutput),
            "dry-run": _getterSetter(getter=self.dryRun, setter=self.clearOutput),
            "z": _getterSetter(getter=self.getZ, setter=self.setZ),
            "rm-tif": _getterSetter(getter=self.removeTiff, setter=self.setRemoveTiff),
        }
        _TofuOptionLoader.__init__(self, options=options)

    def clearOutput(self, *args, **kwargs):
        self._outputWidget.clear()

    def _setImg(self, plane):
        assert plane in ("XY", "XZ", "YZ", "manual")
        self._planeDisplay.setImage(plane + "_lamino")

    def loadFromScan(self, scanID):
        self.__scanID = scanID
        self._updateOutput()

    def _updateOutput(self):
        if self.__scanID is None:
            return
        try:
            if self.isOutputFolderLocked() is False:
                self.setOutput(os.path.join(self.__scanID, self._getNameExtension()))
        except Exception as error:
            _logger.error(error)

    def setPlane(self, plane):
        self._volumeAngleGrp._grpPlane.setPlane(plane=plane)

    def _getNameExtension(self):
        """Return the default name extension according to the scan type"""
        if self._scan_type == SLICE_STACK_TYPE:
            if self._volumeAngleGrp._grpPlane.getPlane() == "XY":
                return "xySlice"
            elif self._volumeAngleGrp._grpPlane.getPlane() == "XZ":
                return "xzSlice"
            elif self._volumeAngleGrp._grpPlane.getPlane() == "YZ":
                return "yzSlice"
            elif self._volumeAngleGrp._grpPlane.getPlane() == "manual":
                return "Slice"
        elif self._scan_type == ROTATION_CENTER_TYPE:
            return "xCenter"
        elif self._scan_type == LAMINO_ANGLE_TYPE:
            return "ctAngle"
        elif self._scan_type in (PSI_ANGLE_TYPE, "psi angle"):
            return "rotC"
        else:
            return "Slice"

    def _setScanType(self, scan_type):
        self._scan_type = scan_type
        illustration = scan_type
        if illustration == "slice stack":
            if self._volumeAngleGrp._grpPlane.getPlane() == "XY":
                illustration = "xy slice"
            elif self._volumeAngleGrp._grpPlane.getPlane() == "XZ":
                illustration = "xz slice"
            elif self._volumeAngleGrp._grpPlane.getPlane() == "YZ":
                illustration = "yz slice"
            elif self._volumeAngleGrp._grpPlane.getPlane() == "manual":
                illustration = "manual slice"
        self._planeDisplay.setImage(illustration)

        self._updateOutput()


class PlaneGroup(qt.QGroupBox):

    sigPlaneChanged = qt.Signal(str)
    """Signal emitted when the plane selection changed"""

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent=parent, title="Plane selection")

        self.setLayout(qt.QVBoxLayout())
        self._XYPlaneRB = qt.QRadioButton("XY", parent=self)
        self.layout().addWidget(self._XYPlaneRB)
        self._YZPlaneRB = qt.QRadioButton("YZ", parent=self)
        self.layout().addWidget(self._YZPlaneRB)
        self._XZPlaneRB = qt.QRadioButton("XZ", parent=self)
        self.layout().addWidget(self._XZPlaneRB)
        self._autoPlaneRB = qt.QRadioButton("manual", parent=self)
        self.layout().addWidget(self._autoPlaneRB)

        self._rBtns = (
            self._XYPlaneRB,
            self._XZPlaneRB,
            self._YZPlaneRB,
            self._autoPlaneRB,
        )
        self._XYPlaneRB.setChecked(True)

        for btn in self._rBtns:
            btn.toggled.connect(self.__planeChangedCllbck)

            self.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Preferred)

    def getPlane(self):
        if self._XYPlaneRB.isChecked():
            return "XY"
        if self._YZPlaneRB.isChecked():
            return "YZ"
        if self._XZPlaneRB.isChecked():
            return "XZ"
        if self._autoPlaneRB.isChecked():
            return "manual"

    def setPlane(self, plane):
        assert plane in ("XY", "XZ", "YZ", "manual")
        for w in self._rBtns:
            w.blockSignals(True)
        if plane == "XY":
            self._XYPlaneRB.setChecked(True)
        elif plane == "XZ":
            self._XZPlaneRB.setChecked(True)
        elif plane == "YZ":
            self._YZPlaneRB.setChecked(True)
        else:
            self._autoPlaneRB.setChecked(True)
        self.sigPlaneChanged.emit(plane)
        for w in self._rBtns:
            w.blockSignals(False)

    def __planeChangedCllbck(self):
        self.sigPlaneChanged.emit(self.getPlane())

    def setManualEdition(self):
        self._autoPlaneRB.setChecked(True)


class VolumeAnglesWidget(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        self._grpPlane = PlaneGroup(parent=self)
        self.layout().addWidget(self._grpPlane)
        self._angles = _AnglesWidget(parent=self)
        self.layout().addWidget(self._angles)

        # API exposed
        self.sigPlaneChanged = self._grpPlane.sigPlaneChanged
        self.sigAnglesEdited = self._angles.sigAnglesEdited

        self.sigAnglesEdited.connect(self._grpPlane.setManualEdition)
        self.sigPlaneChanged.connect(self._resetAngleFor)

        self.setAngles = self._angles.set
        self.getAngles = self._angles.get
        self.setVolumeAngleX = self._angles.setVolumeAngleX
        self.setVolumeAngleY = self._angles.setVolumeAngleY
        self.setVolumeAngleZ = self._angles.setVolumeAngleZ
        self.getVolumeAngleX = self._angles.getVolumeAngleX
        self.getVolumeAngleY = self._angles.getVolumeAngleY
        self.getVolumeAngleZ = self._angles.getVolumeAngleZ

    def _resetAngleFor(self, plane):
        assert plane in ("XY", "XZ", "YZ", "manual")
        if plane == "manual":
            return

        if plane == "XY":
            self._angles.set(0, 0, 0)
        if plane == "XZ":
            self._angles.set(90, 0, 0)
        if plane == "YZ":
            self._angles.set(0, 90, 0)


class _AnglesWidget(qt.QWidget):
    sigAnglesEdited = qt.Signal()
    """Signal emitted when an angle is edited"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._spacerTop = qt.QWidget(parent=self)
        self._spacerTop.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(self._spacerTop)

        self._volAngleX = _AngleWidget(parent=self, name="volume angle x")
        self.layout().addWidget(self._volAngleX)
        self._volAngleY = _AngleWidget(parent=self, name="volume angle y")
        self.layout().addWidget(self._volAngleY)
        self._volAngleZ = _AngleWidget(parent=self, name="volume angle z")
        self.layout().addWidget(self._volAngleZ)
        self._spacerBot = qt.QWidget(parent=self)
        self._spacerBot.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(self._spacerBot)

        self._volAngleX.sigEdited.connect(self._haveBeenEdited)
        self._volAngleY.sigEdited.connect(self._haveBeenEdited)
        self._volAngleZ.sigEdited.connect(self._haveBeenEdited)

        # aliases
        self.setVolumeAngleX = self._volAngleX.setAngle
        self.setVolumeAngleY = self._volAngleY.setAngle
        self.setVolumeAngleZ = self._volAngleZ.setAngle
        self.getVolumeAngleX = self._volAngleX.getAngle
        self.getVolumeAngleY = self._volAngleY.getAngle
        self.getVolumeAngleZ = self._volAngleZ.getAngle

    def _haveBeenEdited(self):
        self.sigAnglesEdited.emit()

    def set(self, xAngle, yAngle, zAngle):
        self.blockSignals(True)
        self.setVolumeAngleX(xAngle)
        self.setVolumeAngleY(yAngle)
        self.setVolumeAngleZ(zAngle)
        self.blockSignals(False)

    def get(self):
        """

        :return: tuple of (anglex, angley, anglez)
        """
        return (
            self._volAngleX.getAngle(),
            self._volAngleY.getAngle(),
            self._volAngleZ.getAngle(),
        )


class StepGroup(qt.QGroupBox):
    sigSelectionChanged = qt.Signal()
    """Signal emitted when the selection changed"""

    _NB_SLICE_NAME = "number of slices"
    _RANGE_NAME = "range"

    _TITLE = "Cut selection"

    def __init__(self, parent):
        qt.QGroupBox.__init__(self, parent=parent, title=StepGroup._TITLE)
        self._xcenter = 0.0
        self.__mediumLimit = settings._N_SLICE_LIMITS_MEDIUM
        self.__highLimit = settings._N_SLICE_LIMITS_HIGH

        self._defaultStyleSheet = ""
        self._mediumLimitStyleSheet = (
            "QLineEdit {" + self._convertToStyleSheetColor(settings._COLOR_MEDIUM) + "}"
        )
        self._highLimitStyleSheet = (
            "QLineEdit {" + self._convertToStyleSheetColor(settings._COLOR_HIGH) + "}"
        )

        self.setLayout(qt.QGridLayout())

        # z
        self._z_label = qt.QLabel("z", parent=self)
        self.layout().addWidget(self._z_label, 0, 0)
        self._zSB = qt.QSpinBox(parent=self)
        self._zSB.setMinimum(-99999)
        self._zSB.setValue(0)
        self.layout().addWidget(self._zSB, 0, 1)

        # step size
        self._stepLabel = qt.QLabel("", parent=self)
        self.layout().addWidget(self._stepLabel, 1, 0)

        self._stepSize = qt.QLineEdit("1.0", parent=self)
        validator = qt.QDoubleValidator(parent=self._stepSize)
        validator.setBottom(0)
        self._stepSize.setValidator(validator)
        self.layout().addWidget(self._stepSize, 1, 1, 1, 6)

        style = qt.QApplication.style()
        icon = style.standardIcon(qt.QStyle.SP_MessageBoxWarning)
        self._warningLabel = qt.QLabel("", parent=self)
        self._warningLabel.setPixmap(icon.pixmap(30, state=qt.QIcon.On))
        self._warningLabel.setVisible(False)
        self._warningLabel.setToolTip(
            "Number of slice to reconstruct seems to high, might fail"
        )

        self.layout().addWidget(self._warningLabel, 1, 7, 1, 1)

        # selection mode
        self.layout().addWidget(qt.QLabel("selection mode:"), 2, 0)
        self._selModeTooltips = {
            self._NB_SLICE_NAME: "Will pick n slices from centered in the center, "
            "spaced of step size",
            self._RANGE_NAME: "Will pick slices from a range, each spaced of "
            "step size",
        }
        self._selectionMode = qt.QComboBox(parent=self)
        self._selectionMode.addItem(self._NB_SLICE_NAME)
        idx = self._selectionMode.findText(self._NB_SLICE_NAME)
        self._selectionMode.setItemData(
            idx, self._selModeTooltips[self._NB_SLICE_NAME], qt.Qt.ToolTipRole
        )
        self._selectionMode.addItem(self._RANGE_NAME)
        idx = self._selectionMode.findText(self._RANGE_NAME)
        self._selectionMode.setItemData(
            idx, self._selModeTooltips[self._RANGE_NAME], qt.Qt.ToolTipRole
        )
        self.layout().addWidget(self._selectionMode, 2, 1)

        self._nCutLE = qt.QLineEdit(str(-settings.SLICE_STACK_STEP_SIZE), self)
        validator = qt.QIntValidator(parent=self._nCutLE)
        validator.setBottom(1)
        self._nCutLE.setValidator(validator)
        self.layout().addWidget(self._nCutLE, 2, 2)

        self._fromLabel = qt.QLabel("from:", self)
        self.layout().addWidget(self._fromLabel, 2, 3)
        self._fromLE = qt.QLineEdit(str(-settings.SLICE_STACK_RANGE_HS), self)
        validator = qt.QDoubleValidator(parent=self._fromLE)
        self._fromLE.setValidator(validator)
        self.layout().addWidget(self._fromLE, 2, 4)
        self._toLabel = qt.QLabel("to:", self)
        self.layout().addWidget(self._toLabel, 2, 5)
        self._toLE = qt.QLineEdit(str(settings.SLICE_STACK_RANGE_HS), self)
        validator = qt.QDoubleValidator(parent=self._toLE)
        self._toLE.setValidator(validator)
        self.layout().addWidget(self._toLE, 2, 6)

        self.setRegionSelType(self._RANGE_NAME)
        self._selectionMode.currentIndexChanged[str].connect(self.setRegionSelType)
        self._setStepSizeType("(pixel)")

        # connect signals / SLOT
        for widget in (self._nCutLE, self._stepSize, self._toLE, self._fromLE):
            widget.textChanged.connect(self._updateLimitsColor)

    @staticmethod
    def _convertToStyleSheetColor(color):
        assert type(color) is tuple
        _color = []
        [_color.append(str(c)) for c in color]
        return "color: rgb(" + ",".join(_color) + ")"

    def _setStepSizeType(self, _type):
        assert type(_type) is str
        self._stepLabel.setText(" ".join(("Step size -", DELTA_CHAR, _type)))

    def setRegionSelType(self, selType):
        """

        :param str selType: should be in ('range', 'number of cut')
        """
        assert selType in (self._RANGE_NAME, self._NB_SLICE_NAME)
        index = self._selectionMode.findText(selType)
        assert index >= 0
        self._selectionMode.blockSignals(True)
        self._selectionMode.setCurrentIndex(index)
        self._selectionMode.setToolTip(self._selModeTooltips[selType])
        for w in (self._fromLE, self._toLE, self._toLabel, self._fromLabel):
            w.setVisible(selType == self._RANGE_NAME)
        self._nCutLE.setVisible(selType == self._NB_SLICE_NAME)
        self._selectionMode.blockSignals(False)
        self.sigSelectionChanged.emit()

    def getSelectionType(self):
        """Return active selected mode ('range' or 'number of cut')"""
        return self._selectionMode.currentText()

    def getStepSize(self):
        """Return step size in fofu ref (meter)"""
        return float(self._stepSize.text())

    def getNCut(self):
        if self.getSelectionType() != self._NB_SLICE_NAME:
            return None
        else:
            return int(self._nCutLE.text())

    def setNCut(self, ncut):
        self._nCutLE.setText(str(ncut))

    def getRegion(self):
        if self.getSelectionType() == self._NB_SLICE_NAME:
            start_from = self._xcenter
            if self._zSB.isVisible() is True:
                start_from = self.getZ() or 0.0
            nbCut = self.getNCut()
            _from = -nbCut / 2 * self.getStepSize() + start_from
            _to = nbCut / 2 * self.getStepSize() + start_from
            return _from, _to, self.getStepSize()
        else:
            start_from = 0.0
            if self._zSB.isVisible() is True:
                start_from = self.getZ() or 0.0
            # question: are from, to always integers ?
            return (
                float(self._fromLE.text()) + start_from,
                float(self._toLE.text()) + start_from,
                float(self.getStepSize()),
            )

    def setRegion(self, region):
        if type(region) is str:
            try:
                _from, _to, step_size = region.split(",")
            except Exception:
                _logger.warning(
                    "Fail to setRegion range. given string "
                    "does not fir the standard (from, to, stepSize)"
                )
                return
        else:
            assert type(region) is tuple
            _from, _to, step_size = region
            _from, _to, step_size = str(_from), str(_to), str(step_size)

        self._fromLE.setText(_from)
        self._toLE.setText(_to)
        self._stepSize.setText(step_size)

    def _updateLimitsColor(self, *argv, **kwargs):
        warning = False
        if self._isUpperHightLimit() is True:
            styleSheet = self._highLimitStyleSheet
            warning = True
        elif self._isUpperMediumLimit() is True:
            styleSheet = self._mediumLimitStyleSheet
            warning = True
        else:
            styleSheet = self._defaultStyleSheet

        for widget in (self._fromLE, self._toLE, self._nCutLE, self._stepSize):
            widget.blockSignals(True)

        self.setStyleSheet(styleSheet)

        for widget in (self._fromLE, self._toLE, self._nCutLE, self._stepSize):
            widget.blockSignals(False)

        self._warningLabel.setVisible(warning)

    def _isUpperMediumLimit(self):
        return self._getNSlices() > self.__mediumLimit

    def _isUpperHightLimit(self):
        return self._getNSlices() > self.__highLimit

    def _getNSlices(self):
        """

        :return: number of slice to be reconstructed
        :rtype: int
        """
        if self.getSelectionType() == self._NB_SLICE_NAME:
            return self.getNCut()
        else:
            # as this cast is made during edition, several value can fail on the
            # float conversion or division
            try:
                _from = float(self._fromLE.text())
                _to = float(self._toLE.text())
                _step = float(self.getStepSize())
                return int((_to - _from) / _step)
            except Exception:
                return 1.0

    def setHighLimit(self, val):
        if val == self.__highLimit:
            return
        if val is None:
            self.resetHighLimit()
            return
        if val <= 0.0:
            _logger.error("incoherent height limit: %s" % val)
            return

        self.__highLimit = val
        self._updateLimitsColor()

    def resetHighLimit(self):
        self.__highLimit = settings._N_SLICE_LIMITS_HIGH
        self._updateLimitsColor()

    def getZ(self):
        if self._zSB.isVisible():
            return self._zSB.value()
        else:
            return None

    def setZ(self, value):
        if value is None:
            return
        return self._zSB.setValue(int(value))

    def _setXCenter(self, xcenter):
        self._xcenter = xcenter


class RegionGB(qt.QGroupBox):
    def __init__(self, parent):
        super().__init__("ROI", parent=parent)
        self.setLayout(qt.QVBoxLayout())
        self._xRegion = _RegionLE(name="x ROI", parent=self)
        self.layout().addWidget(self._xRegion)
        self._yRegion = _RegionLE(name="y ROI", parent=self)
        self.layout().addWidget(self._yRegion)

        # expose API
        self.getXRegion = self._xRegion.getRegion
        self.getYRegion = self._yRegion.getRegion
        self.setXRegion = self._xRegion.setRegion
        self.setYRegion = self._yRegion.setRegion
        self.setXRegionFrmStr = self._xRegion.setRegionFromStr
        self.setYRegionFrmStr = self._yRegion.setRegionFromStr


class _OutputPathWidget(qt.QGroupBox):
    class _OptionsWidget(qt.QWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.setLayout(qt.QHBoxLayout())
            self.layout().setContentsMargins(0, 0, 0, 0)

            self.forceLbsram = qt.QCheckBox("force lbsram", parent=self)
            self.forceLbsram.setToolTip("Make sure reconstruction is saved in lbsram")
            self.layout().addWidget(self.forceLbsram)
            self.forceLbsram.setVisible(os.path.exists(get_lbsram_path()))

            self.removeExisting = qt.QCheckBox('rm "*.tif"', parent=self)
            self.removeExisting.setToolTip("Remove existing files if any")
            self.layout().addWidget(self.removeExisting)
            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
            self.layout().addWidget(spacer)

    def __init__(self, parent):
        super().__init__("output folder", parent)
        self.setLayout(qt.QVBoxLayout())
        self.layout().setContentsMargins(4, 4, 4, 4)

        self._checkboxWidget = _OutputPathWidget._OptionsWidget(parent=self)
        self.layout().addWidget(self._checkboxWidget)

        self._qteFolderSelected = qt.QLineEdit("", parent=self)
        style = qt.QApplication.style()
        icon = style.standardIcon(qt.QStyle.SP_DialogOpenButton)
        self._qtbSelectFolder = qt.QPushButton(icon, "", parent=self)
        self._qteFolderSelected.setToolTip(
            "If not output folder is given, then" ' this will generate a "dry run"'
        )

        self._lockButton = PadlockButton(parent=self)
        self._lockButton.toggled.connect(self._dealWithLbsramOptAndLocker)

        leWidget = qt.QWidget(parent=self)
        leWidget.setLayout(qt.QHBoxLayout())
        leWidget.layout().setContentsMargins(0, 0, 0, 0)
        leWidget.layout().addWidget(self._qteFolderSelected)
        leWidget.layout().addWidget(self._qtbSelectFolder)
        leWidget.layout().addWidget(self._lockButton)
        self.layout().addWidget(leWidget)

        # connect signals/SLOT
        self._checkboxWidget.forceLbsram.toggled.connect(self._updateLbsramStatus)
        self._qtbSelectFolder.clicked.connect(self._setFolderPathFrmDiag)
        self._qteFolderSelected.editingFinished.connect(self._checkUpdateforLbsram)

        # add some speaking API
        self.clear = self._qteFolderSelected.clear
        self.isLocked = self._lockButton.isLocked
        self.forceLbsram = self._checkboxWidget.forceLbsram.isChecked
        self.setForceLbsram = self._checkboxWidget.forceLbsram.setChecked
        self.removeIfExist = self._checkboxWidget.removeExisting.isChecked
        self.setRemoveIfExist = self._checkboxWidget.removeExisting.setChecked

    def setOutput(self, text):
        if self.forceLbsram() is True and text.startswith(get_lbsram_path()) is False:
            text = os.path.join(get_lbsram_path(), text.lstrip(os.sep))
        self._qteFolderSelected.setText(text)

    def lock(self, lock=True):
        self._lockButton.setChecked(lock)

    def _setFolderPathFrmDiag(self):
        dialog = qt.QFileDialog(self)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_() or (len(dialog.selectedFiles()) < 1):
            dialog.close()
            return
        self._qteFolderSelected.setText(dialog.selectedFiles()[0])

    def dryRun(self):
        """Should we execute a dry-run and avoid storing reconstruction"""
        return self.getOutput() is None

    def getOutput(self):
        """Return output folder whre the reconstruction should be saved"""
        if self._qteFolderSelected.text() == "":
            return None
        else:
            return self.__getOutputWithLbsramExtension()

    def _dealWithLbsramOptAndLocker(self, toggle):
        self._checkboxWidget.forceLbsram.setDisabled(toggle)
        if toggle:
            self._checkboxWidget.forceLbsram.setChecked(False)

    def _updateLbsramStatus(self, toggle):
        if toggle is True:
            self._qteFolderSelected.setText(self.__getOutputWithLbsramExtension())

    def __getOutputWithLbsramExtension(self):
        _output = self._qteFolderSelected.text()
        if (
            self.forceLbsram() is True
            and _output.startswith(get_lbsram_path()) is False
        ):
            _output = os.path.join(get_lbsram_path(), _output.lstrip(os.sep))
        return _output

    def _checkUpdateforLbsram(self):
        """Check if the line edit value has to be changed if force lbsram is
        active and the line does not start with it"""
        if self.forceLbsram() is True:
            if not self._qteFolderSelected.text().startswith(get_lbsram_path()):
                self._qteFolderSelected.setText(self.__getOutputWithLbsramExtension())
