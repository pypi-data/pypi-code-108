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
contains gui for diffviewer shift
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/12/2021"


from silx.gui import qt
from silx.utils.enum import Enum as _Enum
import sys
from tomwer.utils import docstring


class _FrameShiftsBase:
    """dummy interface to define how to retrieve shift value"""

    def isFrameALRFlip(self) -> bool:
        """

        :return: True if the frame A should be left-right shift
        """
        raise NotImplementedError

    def getFrameAShift(self) -> tuple:
        """

        :return:
        """
        raise NotImplementedError

    def isFrameBLRFlip(self) -> bool:
        """

        :return: True if the frame B should be left-right shift
        """
        raise NotImplementedError

    def getFrameBShift(self) -> tuple:
        """

        :return:
        """
        raise NotImplementedError


class TwoFramesShiftTab(qt.QTabWidget, _FrameShiftsBase):
    sigShiftsChanged = qt.Signal(tuple)
    """Signal emit when the shift changed. Tuple contains
     shift_imgA, shift_imgB.
     Both are tuple of (x, y, lrflip) x and y are shift values as float.
     lrflip is a boolean notifying if we should flip image or not before applying the shift
    """

    class ShiftMode(_Enum):
        RELATIVE = "relative shift"
        ABSOLUTE = "absolute shift"

    def __init__(self, parent=None):
        super().__init__(parent)
        # create layout
        self._relativeShiftWidget = Relative2FramesShift(self)
        self.addTab(self._relativeShiftWidget, self.ShiftMode.RELATIVE.value)
        self._absoluteShiftWidget = Absolute2FramesShift(self)
        self.addTab(self._absoluteShiftWidget, self.ShiftMode.ABSOLUTE.value)
        # connect signal / slot
        self._absoluteShiftWidget.sigShiftsChanged.connect(self._propagateSignal)
        self._relativeShiftWidget.sigShiftsChanged.connect(self._propagateSignal)
        # set up
        self.setCurrentWidget(self._relativeShiftWidget)
        self._relativeShiftWidget.setFocus(qt.Qt.OtherFocusReason)
        self._relativeShiftWidget.setFocusPolicy(qt.Qt.StrongFocus)
        self.setFocusProxy(self._relativeShiftWidget)

    def getRelativeShiftWidget(self):
        return self._relativeShiftWidget

    def _propagateSignal(self, shift_infos: tuple):
        self.sigShiftsChanged.emit(shift_infos)

    def getShiftMode(self):
        if self.currentWidget() is self._relativeShiftWidget:
            return self.ShiftMode.RELATIVE
        elif self.currentWidget() is self._absoluteShiftWidget:
            return self.ShiftMode.ABSOLUTE
        else:
            raise NotImplementedError("mode not handled")

    @docstring(_FrameShiftsBase)
    def isFrameALRFlip(self) -> bool:
        if self.getShiftMode() is self.ShiftMode.ABSOLUTE:
            return self._absoluteShiftWidget.isFrameALRFlip()
        elif self.getShiftMode() is self.ShiftMode.RELATIVE:
            return self._relativeShiftWidget.isFrameALRFlip()
        else:
            raise NotImplementedError("mode not handled")

    @docstring(_FrameShiftsBase)
    def getFrameAShift(self) -> tuple:
        if self.getShiftMode() is self.ShiftMode.ABSOLUTE:
            return self._absoluteShiftWidget.getFrameAShift()
        elif self.getShiftMode() is self.ShiftMode.RELATIVE:
            return self._relativeShiftWidget.getFrameAShift()
        else:
            raise NotImplementedError("mode not handled")

    @docstring(_FrameShiftsBase)
    def isFrameBLRFlip(self) -> bool:
        if self.getShiftMode() is self.ShiftMode.ABSOLUTE:
            return self._absoluteShiftWidget.isFrameBLRFlip()
        elif self.getShiftMode() is self.ShiftMode.RELATIVE:
            return self._relativeShiftWidget.isFrameBLRFlip()
        else:
            raise NotImplementedError("mode not handled")

    @docstring(_FrameShiftsBase)
    def getFrameBShift(self) -> tuple:
        if self.getShiftMode() is self.ShiftMode.ABSOLUTE:
            return self._absoluteShiftWidget.getFrameBShift()
        elif self.getShiftMode() is self.ShiftMode.RELATIVE:
            return self._relativeShiftWidget.getFrameBShift()
        else:
            raise NotImplementedError("mode not handled")


class Relative2FramesShift(qt.QWidget, _FrameShiftsBase):
    sigShiftsChanged = qt.Signal(tuple)
    """Signal emit when the shift changed. Tuple contains
     shift_imgA, shift_imgB.
     Both are tuple of (x, y, lrflip) x and y are shift values as float.
     lrflip is a boolean notifying if we should flip image or not before applying the shift
    """

    DEFAULT_SINGLE_STEP = 0.5

    MIN_SINGLE_STEP = 0.0001
    MAX_SINGLE_STEP = 1000

    RANGE_MIN_VALUE = -sys.float_info.max
    RANGE_MAX_VALUE = sys.float_info.max

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qt.QHBoxLayout())
        # left spacer
        self._lSpacer = qt.QWidget(self)
        self.layout().addWidget(self._lSpacer)
        # define shift info (x and y shift, x-y shift)
        self._infoWidget = qt.QWidget(self)
        self._infoWidget.setLayout(qt.QFormLayout())
        tSpacer = qt.QWidget(self)
        tSpacer.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding
        )
        self._infoWidget.layout().addRow(tSpacer)
        self._shiftsWidget = qt.QWidget(self)
        self._shiftsWidget.setLayout(qt.QHBoxLayout())
        self._shiftsWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._infoLabel = qt.QLabel(
            "note: This apply x shift on frame A. Frame B will be left-right flip and a -x shit and y shift are applied",
            self,
        )
        font = self._infoLabel.font()
        font.setPixelSize(14)
        font.setItalic(True)
        self._infoLabel.setFont(font)
        self._infoLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self._infoWidget.layout().addRow(self._infoLabel)
        self._infoWidget.layout().addRow("shift", self._shiftsWidget)
        self._xShiftQLE = qt.QDoubleSpinBox(self)
        self._xShiftQLE.setPrefix("x:")
        self._xShiftQLE.setSuffix("px")
        self._xShiftQLE.setRange(self.RANGE_MIN_VALUE, self.RANGE_MAX_VALUE)
        self._yShiftQLE = qt.QDoubleSpinBox(self)
        self._yShiftQLE.setPrefix("y:")
        self._yShiftQLE.setSuffix("px")
        self._yShiftQLE.setRange(self.RANGE_MIN_VALUE, self.RANGE_MAX_VALUE)
        self._shiftsWidget.layout().addWidget(self._xShiftQLE)
        self._shiftsWidget.layout().addWidget(self._yShiftQLE)
        self.layout().addWidget(self._infoWidget)
        self._shiftStepSize = qt.QDoubleSpinBox(self)
        self._shiftStepSize.setValue(1)
        self._shiftStepSize.setRange(self.MIN_SINGLE_STEP, self.MAX_SINGLE_STEP)
        self._infoWidget.layout().addRow("steps", self._shiftStepSize)
        bSpacer = qt.QWidget(self)
        bSpacer.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding
        )
        self._infoWidget.layout().addRow(bSpacer)

        # define control arrows
        self._controlWidget = _ControlArrowWidget(self)
        self._controlWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._controlWidget)
        # right spacer
        self._rSpacer = qt.QWidget(self)
        self.layout().addWidget(self._rSpacer)

        # connect signal / slot
        self._controlWidget.sigMoved.connect(self.move)
        self._xShiftQLE.valueChanged.connect(self._emitHasMoved)
        self._yShiftQLE.valueChanged.connect(self._emitHasMoved)
        self._shiftStepSize.valueChanged.connect(self._stepSizeChanged)

        # set up
        self._controlWidget.setFocusPolicy(qt.Qt.StrongFocus)
        self._controlWidget.setFocus(qt.Qt.OtherFocusReason)

    def move(self, direction: str):
        direction = _ControlArrowWidget.Direction.from_value(direction)
        shift = self._shiftStepSize.value()
        if direction is _ControlArrowWidget.Direction.RIGHT:
            self._xShiftQLE.setValue(self._xShiftQLE.value() + shift)
        elif direction is _ControlArrowWidget.Direction.LEFT:
            self._xShiftQLE.setValue(self._xShiftQLE.value() - shift)
        if direction is _ControlArrowWidget.Direction.UP:
            self._yShiftQLE.setValue(self._yShiftQLE.value() + shift)
        elif direction is _ControlArrowWidget.Direction.DOWN:
            self._yShiftQLE.setValue(self._yShiftQLE.value() - shift)
        old = self.blockSignals(True)
        self.blockSignals(old)
        self._emitHasMoved()

    def _emitHasMoved(self):
        self.sigShiftsChanged.emit(
            (
                (
                    self.getFrameAXShift(),
                    self.getFrameAYShift(),
                    self.isFrameALRFlip(),
                ),
                (
                    self.getFrameBXShift(),
                    self.getFrameBYShift(),
                    self.isFrameBLRFlip(),
                ),
            )
        )

    def getFrameAXShift(self):
        return self._xShiftQLE.value()

    def getFrameAYShift(self):
        # to me does not make sense to have a up / down flip
        # neither than having the same shift or an inverted one.
        # so shift will always be apply on frame only B
        return 0

    def getFrameBXShift(self):
        return -self._xShiftQLE.value()

    def getFrameBYShift(self):
        return self._yShiftQLE.value()

    @docstring(_FrameShiftsBase)
    def isFrameALRFlip(self) -> bool:
        return False  # lr flip by default

    @docstring(_FrameShiftsBase)
    def getFrameAShift(self) -> tuple:
        return (
            self.getFrameAXShift(),
            self.getFrameAYShift(),
        )

    @docstring(_FrameShiftsBase)
    def isFrameBLRFlip(self) -> bool:
        return True  # lr flip by default

    @docstring(_FrameShiftsBase)
    def getFrameBShift(self) -> tuple:
        return (
            self.getFrameBXShift(),
            self.getFrameBYShift(),
        )

    def _stepSizeChanged(self, step):
        self._xShiftQLE.setSingleStep(step)
        self._yShiftQLE.setSingleStep(step)

    def keyPressEvent(self, event):
        self._controlWidget.keyPressEvent(event=event)

    def setShiftStep(self, step):
        self._shiftStepSize.setValue(step)


class _ControlArrowWidget(qt.QWidget):
    """Widget with arrows"""

    sigMoved = qt.Signal(str)
    """signal emit when one direction is activated. Will contain the direction in which we want to move"""

    class Direction(_Enum):
        LEFT = "left"
        RIGHT = "right"
        UP = "up"
        DOWN = "down"

    VALID_DIRECTIONS = Direction.members()

    ARROW_BUTTON_SIZE = 30

    QKEY_TO_DIR = {
        qt.Qt.Key_Left: Direction.LEFT,
        qt.Qt.Key_Right: Direction.RIGHT,
        qt.Qt.Key_Up: Direction.UP,
        qt.Qt.Key_Down: Direction.DOWN,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qt.QGridLayout())
        style = qt.QApplication.style()
        # left arrow
        self._leftArrow = qt.QPushButton()
        self._leftArrow.setIcon(style.standardIcon(qt.QStyle.SP_ArrowLeft))
        self._leftArrow.setMinimumSize(
            qt.QSize(self.ARROW_BUTTON_SIZE, self.ARROW_BUTTON_SIZE)
        )
        self.layout().addWidget(self._leftArrow, 1, 0, 1, 1)
        # right arrow
        self._rightArrow = qt.QPushButton()
        self._rightArrow.setIcon(style.standardIcon(qt.QStyle.SP_ArrowRight))
        self._rightArrow.setMinimumSize(
            qt.QSize(self.ARROW_BUTTON_SIZE, self.ARROW_BUTTON_SIZE)
        )
        self.layout().addWidget(self._rightArrow, 1, 3, 1, 1)
        # up arrow
        self._upArrow = qt.QPushButton()
        self._upArrow.setIcon(style.standardIcon(qt.QStyle.SP_ArrowUp))
        self._upArrow.setMinimumSize(
            qt.QSize(self.ARROW_BUTTON_SIZE, self.ARROW_BUTTON_SIZE)
        )
        self.layout().addWidget(self._upArrow, 0, 1, 1, 1)
        # down
        self._downArrow = qt.QPushButton()
        self._downArrow.setIcon(style.standardIcon(qt.QStyle.SP_ArrowDown))
        self._downArrow.setMinimumSize(
            qt.QSize(self.ARROW_BUTTON_SIZE, self.ARROW_BUTTON_SIZE)
        )
        self.layout().addWidget(self._downArrow, 3, 1, 1, 1)

        # connect signal / slot
        self._leftArrow.released.connect(self._leftActivated)
        self._rightArrow.released.connect(self._rightActivated)
        self._upArrow.released.connect(self._upActivated)
        self._downArrow.released.connect(self._downActivated)

        # add keyboard shortcut
        self._leftArrowShortCut = qt.QShortcut(qt.Qt.LeftArrow, self)
        self._leftArrowShortCut.activated.connect(self._leftActivated)

    def _leftActivated(self, *args, **kwargs):
        self.sigMoved.emit(self.Direction.LEFT.value)

    def _rightActivated(self, *args, **kwargs):
        self.sigMoved.emit(self.Direction.RIGHT.value)

    def _upActivated(self, *args, **kwargs):
        self.sigMoved.emit(self.Direction.UP.value)

    def _downActivated(self, *args, **kwargs):
        self.sigMoved.emit(self.Direction.DOWN.value)

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.QKEY_TO_DIR:
            self.sigMoved.emit(self.QKEY_TO_DIR[key].value)


class Absolute2FramesShift(qt.QWidget, _FrameShiftsBase):
    sigShiftsChanged = qt.Signal(tuple)
    """Signal emit when the shift changed. Tuple is (shift_imgA, shift_imgB).
     Both are tuple of (x, y, lrflip) x and y are shift values as float.
     lrflip is a boolean notifying if we should flip image or not before applying the shift
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(qt.QVBoxLayout())
        self._infoLabel = qt.QLabel(
            "note: This apply shift of images and not of the cor. Do not expect to have the same behavior as the Axis widget manual mode",
            self,
        )
        font = self._infoLabel.font()
        font.setPixelSize(14)
        font.setItalic(True)
        self._infoLabel.setFont(font)
        self._infoLabel.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._infoLabel)

        self._frameAShiftWidget = FrameShiftWidget(title="frame A", parent=self)
        self.layout().addWidget(self._frameAShiftWidget)
        self._frameBShiftWidget = FrameShiftWidget(title="frame B", parent=self)
        self.layout().addWidget(self._frameBShiftWidget)
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(
            qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.MinimumExpanding
        )
        self.layout().addWidget(spacer)

        # connect signal / slot
        self._frameAShiftWidget.sigShiftChanged.connect(self._shiftHasChanged)
        self._frameBShiftWidget.sigShiftChanged.connect(self._shiftHasChanged)

    def _shiftHasChanged(self, *args, **kwargs):
        self.sigShiftsChanged.emit(
            (
                (
                    self.getFrameAShift()[0],
                    self.getFrameAShift()[1],
                    self.isFrameALRFlip(),
                ),
                (
                    self.getFrameBShift()[0],
                    self.getFrameBShift()[1],
                    self.isFrameBLRFlip(),
                ),
            ),
        )

    @docstring(_FrameShiftsBase)
    def isFrameALRFlip(self) -> bool:
        return self._frameAShiftWidget.isLRFlip()

    @docstring(_FrameShiftsBase)
    def getFrameAShift(self) -> tuple:
        return (
            self._frameAShiftWidget.getXShift(),
            self._frameAShiftWidget.getYShift(),
        )

    @docstring(_FrameShiftsBase)
    def isFrameBLRFlip(self) -> bool:
        return self._frameBShiftWidget.isLRFlip()

    @docstring(_FrameShiftsBase)
    def getFrameBShift(self) -> tuple:
        return (
            self._frameBShiftWidget.getXShift(),
            self._frameBShiftWidget.getYShift(),
        )


class FrameShiftWidget(qt.QWidget):
    sigShiftChanged = qt.Signal(tuple)
    """Signal emit when the shift changed. Tuple contains (x, y, lrflip)
     x, y values as float and lrflip as boolean"""

    DEFAULT_SINGLE_STEP = 0.5

    MIN_SINGLE_STEP = 0.0001
    MAX_SINGLE_STEP = 1000

    RANGE_MIN_VALUE = -sys.float_info.max
    RANGE_MAX_VALUE = sys.float_info.max

    def __init__(self, title, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(qt.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        # define label
        self._label = qt.QLabel(f"{title} shift", self)
        self._label.setAlignment(qt.Qt.AlignRight | qt.Qt.AlignVCenter)
        self.layout().addWidget(self._label)
        # define x shift
        self._xShiftQDSB = qt.QDoubleSpinBox(self)
        self._xShiftQDSB.setPrefix("x:")
        self._xShiftQDSB.setSuffix("px")
        self._xShiftQDSB.setValue(0)
        self._xShiftQDSB.setRange(self.RANGE_MIN_VALUE, self.RANGE_MAX_VALUE)
        self.layout().addWidget(self._xShiftQDSB)
        # define y shift
        self._yShiftQDSB = qt.QDoubleSpinBox(self)
        self._yShiftQDSB.setPrefix("y:")
        self._yShiftQDSB.setSuffix("px")
        self._yShiftQDSB.setValue(0)
        self._yShiftQDSB.setRange(self.RANGE_MIN_VALUE, self.RANGE_MAX_VALUE)
        self.layout().addWidget(self._yShiftQDSB)
        # reset button
        self._resetPB = qt.QPushButton(self)
        style = qt.QApplication.style()
        resetIcon = style.standardIcon(qt.QStyle.SP_DialogResetButton)
        self._resetPB.setIcon(resetIcon)
        self._resetPB.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        self.layout().addWidget(self._resetPB)
        # shift steps
        self._shiftStepsQDSB = qt.QDoubleSpinBox(self)
        self._shiftStepsQDSB.setPrefix("steps:")
        self._shiftStepsQDSB.setSuffix("px")
        self._shiftStepsQDSB.setValue(1.0)
        self._shiftStepsQDSB.setRange(self.MIN_SINGLE_STEP, self.MAX_SINGLE_STEP)
        self.layout().addWidget(self._shiftStepsQDSB)
        self._shiftStepsQDSB.setRange(0.01, 100000)
        self._shiftStepsQDSB.setSingleStep(0.5)
        # lr flip
        self._lrFlipQCB = qt.QCheckBox("lr flip", self)
        self._lrFlipQCB.setToolTip("left-right flip")
        self.layout().addWidget(self._lrFlipQCB)
        self._lrFlipQCB.setChecked(False)

        # connect signal / slot
        self._resetPB.released.connect(self.clear)
        self._xShiftQDSB.valueChanged.connect(self._shiftHasChanged)
        self._yShiftQDSB.valueChanged.connect(self._shiftHasChanged)
        self._shiftStepsQDSB.valueChanged.connect(self._stepsHasChanged)
        self._lrFlipQCB.toggled.connect(self._shiftHasChanged)

    def _stepsHasChanged(self, *args, **kwargs):
        self._xShiftQDSB.setSingleStep(self.getSingleStep())
        self._yShiftQDSB.setSingleStep(self.getSingleStep())

    def getSingleStep(self):
        return self._shiftStepsQDSB.value()

    def getXShift(self) -> float:
        return self._xShiftQDSB.value()

    def getYShift(self) -> float:
        return self._yShiftQDSB.value()

    def clear(self):
        old = self.blockSignals(True)
        self._xShiftQDSB.setValue(0)
        self._yShiftQDSB.setValue(0)
        self.blockSignals(old)
        self._shiftHasChanged()

    def _shiftHasChanged(self, *args, **kwargs):
        shift = self.getXShift(), self.getYShift()
        self.sigShiftChanged.emit(shift)

    def isLRFlip(self) -> bool:
        return self._lrFlipQCB.isChecked()
