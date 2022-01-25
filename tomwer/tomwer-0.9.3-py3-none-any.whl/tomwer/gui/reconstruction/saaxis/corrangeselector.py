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
contains gui relative to semi-automatic axis calculation
"""


__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "26/02/2021"


from tomwer.gui import icons
from tomwer.core.process.reconstruction.saaxis.saaxis import ReconstructionMode
from tomwer.gui.utils.slider import LogSlider
from tomwer.core.scan.scanbase import TomwerScanBase
from typing import Union
from silx.gui.plot import items
from silx.utils.enum import Enum as _Enum
from tomwer.gui.reconstruction.saaxis.sliceselector import SliceSelector
from tomwer.gui.visualization.sinogramviewer import SinogramViewer as _SinogramViewer
from tomwer.gui.utils.lineselector import QSliceSelectorDialog
from silx.gui import qt, icons as silxicons
from silx.gui.dialog.ImageFileDialog import ImageFileDialog
from silx.io.utils import get_data
import numpy
import weakref
import logging
import functools

_logger = logging.getLogger(__name__)


class DetectionAccuracy(_Enum):
    """The different accuracy modes"""

    COARSE = "Coarse"
    FINE = "Fine"
    ACCURATE = "Accurate"
    DEFINED_RANGE = "Defined range"


ACCURACIES = {
    DetectionAccuracy.COARSE: 500,
    DetectionAccuracy.FINE: 10,
    DetectionAccuracy.ACCURATE: 2,
}


class SinogramViewer(_SinogramViewer):
    """Redefine the main SinogramViewer for saaxis purpose:
    * options orientation is horizontal
    * add the display of the cor roi to be displayed
    * rename ApplyButton to load and change the icon
    * hide the line selection (control by the slice selector
    * move the dock widget to the bottom
    * rename subsampling "loaded sinogram subsampling" to provide more context
    """

    sigCorEdited = qt.Signal(float)
    """Signal emitted when the cor position change. Provided in absolute
    position"""
    sigWidthEdited = qt.Signal(float)
    """Signal emitted when the detection accuracy (width) change."""

    def __init__(self, parent):
        super().__init__(parent, opts_orientation=qt.Qt.Horizontal)
        self._fromMarker = None
        self._toMarker = None
        self._corMarker = None
        self._min = None
        self._max = None
        self._estimated_cor = None
        self._other_cors = None
        # hide line selection
        self._options.setLineSelectionVisible(False)
        # change ApplyButton name and icon
        self._loadButton = self._options._buttons.button(qt.QDialogButtonBox.Apply)
        self._loadButton.setText("load")
        style = qt.QApplication.style()
        self._loadButton.setIcon(style.standardIcon(qt.QStyle.SP_BrowserReload))
        # change subsampling name
        self._options._subsamplingLabel.setText("Sinogram subsampling")
        self._options._subsamplingLabel.setToolTip(
            "Define subsampling of the " "sinogram to be displayed"
        )

    def loadSinogram(self):
        """simulate the click on `load` of the QPushButton"""
        self._loadButton.clicked.emit()

    def getOptionsDockWidget(self):
        return self._dockOpt

    def _updatePlot(self, sinogram):
        super()._updatePlot(sinogram)
        if (
            self._min is not None
            and self._max is not None
            and self._estimated_cor is not None
        ):
            self.setCorRange(
                min=self._min,
                max=self._max,
                estimated_cor=self._estimated_cor,
                other_cors=self._other_cors,
            )

    def setCorRange(self, min, max, estimated_cor, other_cors=tuple()):
        """
        For now we can only modify the estimated cor

        :param float min:
        :param float max:
        :param float estimated_cor:
        :param int display_n_recons: the grid created by all cor observe
        :return:
        """
        self._min = min
        self._max = max
        self._estimated_cor = estimated_cor
        self._other_cors = other_cors if other_cors is not None else tuple()

        plot = self._plot.getPlotWidget()

        if self._corMarker is not None:
            self._corMarker.sigDragFinished.disconnect(self._middleMarkerMoved)
        if self._fromMarker is not None:
            self._fromMarker.sigDragFinished.disconnect(self._fromCallback)
        if self._toMarker is not None:
            self._toMarker.sigDragFinished.disconnect(self._toCallback)

        # clear existing markers
        markers = [
            item.getName()
            for item in plot.getItems()
            if isinstance(item, items.MarkerBase)
        ]
        for marker in markers:
            plot.removeMarker(marker)
        # recreate markers
        plot.addXMarker(
            x=min, legend="from", text="from", color="#3449ebff", draggable=True
        )
        plot.addXMarker(
            x=max, legend="to", text="to", color="#3449ebff", draggable=True
        )
        plot.addXMarker(
            x=estimated_cor,
            legend="estimated cor",
            text="estimated cor",
            color="#34dcebff",
            draggable=True,
        )
        for i_cor, cor in enumerate(other_cors):
            plot.addXMarker(
                x=cor, legend="cor_{}".format(i_cor), draggable=False, color="#34dceb42"
            )

        # handle draggable markers
        self._fromMarker = plot._getMarker("from")
        self._fromCallback = functools.partial(self._limitMarkerMoved, self._fromMarker)
        self._fromMarker.sigDragFinished.connect(self._fromCallback)

        self._toMarker = plot._getMarker("to")
        self._toCallback = functools.partial(self._limitMarkerMoved, self._toMarker)
        self._toMarker.sigDragFinished.connect(self._toCallback)

        self._corMarker = plot._getMarker("estimated cor")
        self._corMarker.sigDragFinished.connect(self._middleMarkerMoved)

    def _middleMarkerMoved(self):
        if self._corMarker is not None:
            self.sigCorEdited.emit(self._corMarker.getXPosition())

    def _limitMarkerMoved(self, marker):
        if self._corMarker is not None and marker is not None:
            new_half_width = numpy.abs(
                marker.getXPosition() - self._corMarker.getXPosition()
            )
            self.sigWidthEdited.emit(new_half_width * 2.0)


class _ReconstructionModeGB(qt.QGroupBox):

    reconstructionModeChanged = qt.Signal(str)

    reconstructionSliceChanged = qt.Signal()

    _DEFAULT_VERTICAL_SLICE_MODE = ("middle", "other")

    def __init__(self, parent=None, title="Slice reconstruction mode"):
        self.__scan = None
        qt.QGroupBox.__init__(self, parent)
        self.setTitle(title)
        self.setLayout(qt.QVBoxLayout())
        self._verticalRB = qt.QRadioButton(ReconstructionMode.VERTICAL.value, self)
        self.layout().addWidget(self._verticalRB)
        self._tiltCorrectionRB = qt.QRadioButton(
            ReconstructionMode.TILT_CORRECTION.value, self
        )
        self.layout().addWidget(self._tiltCorrectionRB)

        # slice choice combobox
        self._defaultSlicesCB = qt.QComboBox(self)
        for mode in self._DEFAULT_VERTICAL_SLICE_MODE:
            self._defaultSlicesCB.addItem(mode)
        self.layout().addWidget(self._defaultSlicesCB)

        # slice selector
        self._sliceVerticalQSB = SliceSelector(self, insert=False, invert_y_axis=True)
        self._sliceVerticalQSB.addSlice(value=0, name="Slice", color="green")
        self._sliceVerticalQSB.setFixedSize(qt.QSize(250, 250))
        self.layout().addWidget(self._sliceVerticalQSB)
        self._sliceTiltCorrQSB = SliceSelector(self, insert=False, invert_y_axis=True)
        self._sliceTiltCorrQSB.addSlice(value=0, name="Slice 0", color="#7e8dff")
        self._sliceTiltCorrQSB.addSlice(value=0, name="Slice 1", color="cyan")
        self._sliceTiltCorrQSB.setFixedSize(qt.QSize(250, 230))
        self.layout().addWidget(self._sliceTiltCorrQSB)
        # select on radio
        # line selector button
        onRadioIcon = silxicons.getQIcon("window-new")
        self._onRadioButton = qt.QPushButton(
            onRadioIcon, "select on radio", parent=self
        )
        self._onRadioButton.setToolTip("Open a dialog to pick the rows from" "a radio")
        self.layout().addWidget(self._onRadioButton)

        # connect signal / slot
        self._verticalRB.toggled.connect(self._reconstructionModeChanged)
        self._tiltCorrectionRB.toggled.connect(self._reconstructionModeChanged)
        self._sliceVerticalQSB.sigSlicesChanged.connect(
            self._reconstructionSliceChanged
        )
        self._onRadioButton.released.connect(self._onRadioActivated)
        self._defaultSlicesCB.currentIndexChanged.connect(self._updateVerticalSelection)

        # set up
        self.blockSignals(True)
        self.setCurrentMode("vertical", "middle")
        self.blockSignals(False)
        # for now we don't have the tilt correction mode
        # self._sliceTiltCorrQSB.hide()
        self._tiltCorrectionRB.hide()

    def setCurrentMode(self, mode, slices):
        valid_modes = ("vertical", "horizontal")
        if mode not in valid_modes:
            raise ValueError(
                "mode {} is not recosgnized. Valid modes are {}"
                "".format(mode, valid_modes)
            )
        self._verticalRB.setChecked(mode == "vertical")
        if mode == "vertical":
            if slices not in self._DEFAULT_VERTICAL_SLICE_MODE:
                raise ValueError(
                    "{} is not a vadid slice mode. Calid are {}"
                    "".format(slices, self._DEFAULT_VERTICAL_SLICE_MODE)
                )
            else:
                index = self._defaultSlicesCB.findText(slices)
                self._defaultSlicesCB.setCurrentIndex(index)
                self._defaultSlicesCB.currentIndexChanged.emit(index)

    def _updateVerticalSelection(self):
        current_mode = self._defaultSlicesCB.currentText()
        mode_is_middle = current_mode == "middle"
        self._sliceVerticalQSB.setVisible(not mode_is_middle)
        self._onRadioButton.setVisible(not mode_is_middle)
        self._reconstructionSliceChanged()

    def _onRadioActivated(self):
        lineSelection = QSliceSelectorDialog(parent=self, n_required_slice=1)
        scan = self.__scan() if self.__scan else None
        if scan is None:
            _logger.info("No scan defined, request user for defining the image" "url")
            dialog = ImageFileDialog()
            if dialog.exec_():
                data = dialog.selectedImage()
            else:
                return
        else:
            assert isinstance(scan, TomwerScanBase)
            try:
                projections = scan.projections
                index_radio = list(projections.keys())[len(projections) // 2]
                data = get_data(projections[index_radio])
            except Exception as e:
                _logger.error("Fail to load radio data:", str(e))
                return

        lineSelection.setData(data)
        lineSelection.setSelection(list(self.getReconstructionSlices().values()))
        if lineSelection.exec_() == qt.QDialog.Accepted:
            selection = lineSelection.getSelection()
            if selection is not None and len(selection) > 0:
                self.setReconstructionSlices({"Slice": selection[0]})

    def setScan(self, scan):
        self.__scan = weakref.ref(scan)

    def _reconstructionSliceChanged(self):
        # for now we only synchronize sliceQSB from vertical with the sinogram
        # viewer
        self.reconstructionSliceChanged.emit()

    def getReconstructionMode(self) -> ReconstructionMode:
        if self._tiltCorrectionRB.isChecked():
            return ReconstructionMode.TILT_CORRECTION
        elif self._verticalRB.isChecked():
            return ReconstructionMode.VERTICAL
        else:
            raise ValueError("No reconstruction mode selected")

    def setReconstructionMode(self, mode: Union[str, ReconstructionMode]) -> None:
        mode = ReconstructionMode.from_value(mode)
        if mode is ReconstructionMode.TILT_CORRECTION:
            self._tiltCorrectionRB.setChecked(True)
        elif mode is ReconstructionMode.VERTICAL:
            self._verticalRB.setChecked(True)
        else:
            raise ValueError("No reconstruction mode selected")

    def getReconstructionSlices(self):
        mode = self.getReconstructionMode()
        if mode is ReconstructionMode.TILT_CORRECTION:
            return self._sliceTiltCorrQSB.getSlicesValue()
        elif mode is ReconstructionMode.VERTICAL:
            if self._defaultSlicesCB.currentText() == "middle":
                return "middle"
            else:
                return self._sliceVerticalQSB.getSlicesValue()
        else:
            raise ValueError("mode {} is not handled".format(mode))

    def setReconstructionSlices(self, slice: Union[dict, int, str]):
        slice_name = None
        if slice == "middle" or isinstance(slice, int) or len(slice) == 1:
            self.setReconstructionMode(ReconstructionMode.VERTICAL)
            target = self._sliceVerticalQSB
            if slice == "middle":
                index = self._defaultSlicesCB.findText("middle")
            else:
                index = self._defaultSlicesCB.findText("other")
                slice_name = "Slice"
            self._defaultSlicesCB.setCurrentIndex(index)
        elif len(slice) == 2:
            self.setReconstructionMode(ReconstructionMode.TILT_CORRECTION)
            target = self._sliceTiltCorrQSB
        else:
            raise ValueError("slice is expected to contain one or two element(s)")
        if slice not in ("middle",):
            if isinstance(slice, int):
                target.setSliceValue(name=slice_name, value=slice)
            else:
                for slice_name, slice_value in slice.items():
                    target.setSliceValue(name=slice_name, value=slice_value)

    def _reconstructionModeChanged(self, *args, **kwargs):
        reconstruction_mode = self.getReconstructionMode()
        self.reconstructionModeChanged.emit(reconstruction_mode.value)
        self._sliceTiltCorrQSB.setVisible(
            reconstruction_mode is ReconstructionMode.TILT_CORRECTION
        )
        self._sliceVerticalQSB.setVisible(
            reconstruction_mode is ReconstructionMode.VERTICAL
        )

    def setSlicesRange(self, min_index, max_index):
        self._sliceTiltCorrQSB.setSlicesRange(min_index, max_index)
        self._sliceVerticalQSB.setSlicesRange(min_index, max_index)

    def getSlicesRange(self):
        return self._sliceVerticalQSB.getSlicesRange()


class _DetectionAccuracyGB(qt.QGroupBox):

    detectionAccuracyChanged = qt.Signal()
    """signal emitted when the value change"""

    _MIN_RANGE = 0.1
    _MAX_RANGE = 4000
    _DEFAULT_VALUE = 10

    def __init__(self, parent=None, title="Detection accuracy (width)"):
        qt.QGroupBox.__init__(self, parent)
        self.setTitle(title)
        self.setLayout(qt.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        # slider
        self._accuracySlider = LogSlider(parent=self)
        self._accuracySlider.setSuffix(" px")
        self.layout().addWidget(self._accuracySlider, 0, 0, 1, 5)
        # different accuracy buttons
        accuracy_opt_font = self.font()
        accuracy_opt_font.setPixelSize(10)
        self._coarsePB = qt.QPushButton(DetectionAccuracy.COARSE.value, self)
        self._coarsePB.setFont(accuracy_opt_font)
        self._coarsePB.setFlat(True)
        self.layout().addWidget(self._coarsePB, 1, 2, 1, 1)
        self._finePB = qt.QPushButton(DetectionAccuracy.FINE.value, self)
        self._finePB.setFont(accuracy_opt_font)
        self._finePB.setFlat(True)
        self.layout().addWidget(self._finePB, 1, 1, 1, 1)
        self._accuratePB = qt.QPushButton(DetectionAccuracy.ACCURATE.value, self)
        self._accuratePB.setFont(accuracy_opt_font)
        self._accuratePB.setFlat(True)
        self.layout().addWidget(self._accuratePB, 1, 0, 1, 1)

        # connect signal / slot
        self._coarsePB.released.connect(self._setCoarse)
        self._finePB.released.connect(self._setFine)
        self._accuratePB.released.connect(self._setAccurate)
        self._accuracySlider.valueChanged.connect(self.detectionAccuracyChanged)

        # set up
        self._accuracySlider.setRange(self._MIN_RANGE, self._MAX_RANGE)
        self._accuracySlider.setValue(self._DEFAULT_VALUE)

    def _detectionAccuracyChanged(self, *args, **kwargs):
        self.detectionAccuracyChanged.emit()

    def getResearchWidth(self) -> float:
        """Return research width (in pixel)"""
        return self._accuracySlider.value()

    def setResearchWidth(self, width: float):
        """set research width

        :param float width: center of rotation research width
        """
        return self._accuracySlider.setValue(width)

    def _setCoarse(self):
        self._accuracySlider.setValue(ACCURACIES[DetectionAccuracy.COARSE])

    def _setFine(self):
        self._accuracySlider.setValue(ACCURACIES[DetectionAccuracy.FINE])

    def _setAccurate(self):
        self._accuracySlider.setValue(ACCURACIES[DetectionAccuracy.ACCURATE])


class _EstimatedCorWidget(qt.QGroupBox):

    _MIDDLE_COR_TXT = "middle"
    _OTHER_COR_TXT = "other"

    sigAutoCorRequested = qt.Signal()
    """signal emitted when the calculation of automatic cor is asked"""

    sigAutoCorChanged = qt.Signal()
    """signal emitted when the estimated cor value change"""

    def __init__(self, parent=None, title=None):
        assert title is not None
        self._frameWidth = None
        qt.QGroupBox.__init__(self, parent)
        self.setTitle(title)
        self.setLayout(qt.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._middlePositionRB = qt.QCheckBox("middle", self)
        self.layout().addWidget(self._middlePositionRB, 0, 0, 1, 2)
        # manual definition of the cor
        self._manualCORAbs = qt.QDoubleSpinBox(self)
        self._manualCORAbs.setDecimals(4)
        self._manualCORAbs.setMaximum(9999999)
        self._manualCORAbs.setSuffix(" px")
        self._absLabel = qt.QLabel("absolute: ")
        self.layout().addWidget(self._absLabel, 1, 0, 1, 1)
        self.layout().addWidget(self._manualCORAbs, 1, 1, 1, 1)
        self._manualCORRel = qt.QDoubleSpinBox(self)
        self._manualCORRel.setDecimals(4)
        self._manualCORRel.setSuffix(" px")
        self._manualCORRel.setMinimum(-9999999)
        self._manualCORRel.setMaximum(9999999)
        self._relLabel = qt.QLabel("relative: ")
        self.layout().addWidget(self._relLabel, 2, 0, 1, 1)
        self.layout().addWidget(self._manualCORRel, 2, 1, 1, 1)
        # auto cor button
        self._autoCorPB = qt.QPushButton("auto cor", self)
        auto_cor_icon = icons.getQIcon("a")
        self._autoCorPB.setIcon(auto_cor_icon)
        self.layout().addWidget(self._autoCorPB, 3, 1, 1, 1)

        # connect signal / slot
        self._middlePositionRB.toggled.connect(self._modeChanged)
        self._manualCORRel.editingFinished.connect(self._relativePositionChanged)
        self._manualCORAbs.editingFinished.connect(self._absolutePositionChanged)
        self._autoCorPB.released.connect(self._autoCorReqested)
        self._middlePositionRB.toggled.connect(self._autoCorValueChanged)
        self._manualCORRel.editingFinished.connect(self._autoCorValueChanged)
        self._manualCORAbs.editingFinished.connect(self._autoCorValueChanged)
        # set up
        self._middlePositionRB.setChecked(True)
        self._modeChanged()

    def getCorValue(self, mode="relative"):
        assert mode in ("rel", "relative", "abs", "absolute")
        if self._middlePositionRB.isChecked():
            if mode in ("rel", "relative"):
                return 0.0
            elif mode in ("abs", "absolute"):
                if self._frameWidth is not None:
                    return self._frameWidth / 2.0
                else:
                    return self._MIDDLE_COR_TXT
            else:
                raise ValueError("Mode {} is not recognized".format(mode))
        else:
            if mode in ("rel", "relative"):
                return self._manualCORRel.value()
            elif mode in ("abs", "absolute"):
                return self._manualCORAbs.value()
            else:
                raise ValueError("Mode {} is not recognized".format(mode))

    def _modeChanged(self, *args, **kwargs):
        manual_opt_visible = not self._middlePositionRB.isChecked()
        self._absLabel.setVisible(manual_opt_visible)
        self._relLabel.setVisible(manual_opt_visible)
        self._manualCORRel.setVisible(manual_opt_visible)
        self._manualCORAbs.setVisible(manual_opt_visible)

    def _relativePositionChanged(self, *args, **kwargs):
        if self._frameWidth is not None:
            old = self.blockSignals(True)
            old_mcor = self._manualCORAbs.blockSignals(True)
            self._manualCORAbs.setValue(
                self._manualCORRel.value() + self._frameWidth / 2.0
            )
            self._manualCORAbs.blockSignals(old_mcor)
            self.blockSignals(old)

    def _absolutePositionChanged(self, *args, **kwargs):
        if self._frameWidth is not None:
            old = self.blockSignals(True)
            old_mcor = self._manualCORRel.blockSignals(True)
            self._manualCORRel.setValue(
                self._manualCORAbs.value() - self._frameWidth / 2.0
            )
            self._manualCORRel.blockSignals(old_mcor)
            self.blockSignals(old)

    def setFrameWidth(self, width):
        self._frameWidth = width
        # if necessary auto reset of the absolute value
        if self._manualCORAbs.value() == self._manualCORRel.value():
            self._relativePositionChanged()

    def getFrameWidth(self):
        return self._frameWidth

    def setCorValue(self, value):
        """

        :param Union[str,float] value: if a float expected to be given as the
                                       relative value
        :return:
        """
        if value == self._MIDDLE_COR_TXT:
            self._middlePositionRB.setChecked(True)
        else:
            self._middlePositionRB.setChecked(False)
            self._manualCORRel.setValue(float(value))
            self._manualCORRel.editingFinished.emit()

    def setAbsoluteCorValue(self, value):
        if value == self._MIDDLE_COR_TXT:
            self._middlePositionRB.setChecked(True)
        else:
            self._middlePositionRB.setChecked(False)
            self._manualCORAbs.setValue(float(value))
            self._manualCORAbs.editingFinished.emit()

    def _autoCorReqested(self):
        self.sigAutoCorRequested.emit()

    def _autoCorValueChanged(self):
        self.sigAutoCorChanged.emit()


class SAAxisOptions(qt.QWidget):
    """
    Options of the semi-automatic center of rotation detection
    """

    sigReconstructionSliceChanged = qt.Signal()
    """signal emitted when the slice to reconstruct change"""

    sigReconstructionRangeChanged = qt.Signal()
    """signal emitted when the reconstruction parameters change"""

    sigConfigurationChanged = qt.Signal()
    """signal emitted when the configuration change"""

    _FONT_IMPORTANT = qt.QFont("Arial", 12)
    _FONT_MEDIUM = qt.QFont("Arial", 10)

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        # reconstruction mode
        self._reconstructionMode = _ReconstructionModeGB(parent=self)
        self._reconstructionMode.setFont(self._FONT_MEDIUM)
        self.layout().addWidget(self._reconstructionMode)

        # estimated cor
        self._estimatedCorWidget = _EstimatedCorWidget(
            self,
            title="Estimated cor position (x axis)",
        )
        self._estimatedCorWidget.setFont(self._FONT_IMPORTANT)
        self.layout().addWidget(self._estimatedCorWidget)

        # detection accuracy
        self._detectionAccuracy = _DetectionAccuracyGB(parent=self)
        self._detectionAccuracy.setFont(self._FONT_MEDIUM)
        self.layout().addWidget(self._detectionAccuracy)

        # number of reconstructions eq volume size
        self._nReconsWidget = qt.QWidget(parent)
        self._nReconsWidget.setLayout(qt.QFormLayout())
        self._nReconsWidget.layout().setContentsMargins(0, 0, 0, 0)
        self._nReconsSB = qt.QSpinBox(self._nReconsWidget)
        self._nReconsSB.setRange(0, 2000)
        self._nReconsSB.setValue(30)
        self._nReconsWidget.setFont(self._FONT_IMPORTANT)
        self._nReconsWidget.layout().addRow("Number of reconstruction", self._nReconsSB)
        self.layout().addWidget(self._nReconsWidget)

        # spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # expose API
        self.sigAutoCorRequested = self._estimatedCorWidget.sigAutoCorRequested

        # connect signal / slot
        self._reconstructionMode.reconstructionSliceChanged.connect(
            self._reconstructionSliceChanged
        )
        self._nReconsSB.valueChanged.connect(self._reconstructionRangeChanged)
        self._estimatedCorWidget.sigAutoCorChanged.connect(
            self._reconstructionRangeChanged
        )
        self._detectionAccuracy.detectionAccuracyChanged.connect(
            self._reconstructionRangeChanged
        )

    def setDetectionAccuracy(self, width):
        if width != self._detectionAccuracy.getResearchWidth():
            self._detectionAccuracy.setResearchWidth(width)
            self.sigConfigurationChanged.emit()

    def setEstimatedCorPosition(self, value):
        if value != self._estimatedCorWidget.getCorValue("relative"):
            self._estimatedCorWidget.setCorValue(value)
            self.sigConfigurationChanged.emit()

    def setEstimatedAbsoluteCorPosition(self, value):
        if value != self._estimatedCorWidget.getCorValue("absolute"):
            self._estimatedCorWidget.setAbsoluteCorValue(value)
            self.sigConfigurationChanged.emit()

    def getEstimatedCorPosition(self, *args, **kwargs):
        return self._estimatedCorWidget.getCorValue(*args, **kwargs)

    def setScan(self, scan: TomwerScanBase):
        if scan is not None:
            self.setSlicesRange(0, scan.dim_2)
            self._estimatedCorWidget.setFrameWidth(scan.dim_1)
            self._reconstructionMode.setScan(scan)

    def getFrameWidth(self):
        return self._estimatedCorWidget.getFrameWidth()

    def setFrameWidth(self, width):
        if width != self._estimatedCorWidget.getFrameWidth():
            self._estimatedCorWidget.setFrameWidth(width)
            self.sigConfigurationChanged.emit()

    def getSlicesRange(self) -> tuple:
        self._reconstructionMode.getSlicesRange()

    def setSlicesRange(self, min_index, max_index):
        self._reconstructionMode.setSlicesRange(min_index, max_index)
        self.sigConfigurationChanged.emit()

    def _reconstructionSliceChanged(self):
        self.sigReconstructionSliceChanged.emit()

    def _reconstructionRangeChanged(self):
        self.sigReconstructionRangeChanged.emit()
        self.sigConfigurationChanged.emit()

    def getReconstructionSlices(self) -> tuple:
        return self._reconstructionMode.getReconstructionSlices()

    def setReconstructionSlices(self, slices) -> tuple:
        return self._reconstructionMode.setReconstructionSlices(slices)

    def getReconstructionMode(self):
        return self._reconstructionMode.getReconstructionMode()

    def setReconstructionMode(self, mode):
        self._reconstructionMode.setReconstructionMode(mode)
        self.sigConfigurationChanged.emit()

    def getNReconstruction(self):
        return self._nReconsSB.value()

    def setNReconstruction(self, n):
        self._nReconsSB.setValue(int(n))
        self.sigConfigurationChanged.emit()

    def getResearchWidth(self):
        return self._detectionAccuracy.getResearchWidth()

    def setResearchWidth(self, width):
        self._detectionAccuracy.setResearchWidth(width)
        self.sigConfigurationChanged.emit()


class SliceAndCorWidget(qt.QMainWindow):
    sigConfigurationChanged = qt.Signal()
    """signal emitted when the configuration changed"""

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        # sinogram viewer
        self._sinogramViewer = SinogramViewer(self)
        self._sinogramViewer.setWindowFlags(qt.Qt.Widget)
        self.setCentralWidget(self._sinogramViewer)
        # slice and accuracy options
        self._saaxisOpts = SAAxisOptions(self)
        self._dockWidgetOpts = qt.QDockWidget(self)
        self._dockWidgetOpts.setFixedWidth(300)
        self._dockWidgetOpts.setWidget(self._saaxisOpts)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._dockWidgetOpts)
        self._dockWidgetOpts.setFeatures(qt.QDockWidget.DockWidgetMovable)
        # sinogram options
        self.sinoOprsDW = self._sinogramViewer.getOptionsDockWidget()
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self.sinoOprsDW)
        self.sinoOprsDW.setFeatures(qt.QDockWidget.DockWidgetMovable)
        self.sinoOprsDW.setFixedWidth(300)

        # expose API
        self.getEstimatedCorPosition = self._saaxisOpts.getEstimatedCorPosition
        self.setEstimatedCorPosition = self._saaxisOpts.setEstimatedCorPosition
        self.setEstimatedAbsoluteCorPosition = (
            self._saaxisOpts.setEstimatedAbsoluteCorPosition
        )
        self.setDetectionAccuracy = self._saaxisOpts.setDetectionAccuracy
        self.getNReconstruction = self._saaxisOpts.getNReconstruction
        self.setNReconstruction = self._saaxisOpts.setNReconstruction
        self.getResearchWidth = self._saaxisOpts.getResearchWidth
        self.setResearchWidth = self._saaxisOpts.setResearchWidth
        self.getReconstructionSlices = self._saaxisOpts.getReconstructionSlices
        self.setReconstructionSlices = self._saaxisOpts.setReconstructionSlices
        self.getReconstructionMode = self._saaxisOpts.getReconstructionMode
        self.setReconstructionMode = self._saaxisOpts.setReconstructionMode
        self.getFrameWidth = self._saaxisOpts.getFrameWidth
        self.setFrameWidth = self._saaxisOpts.setFrameWidth
        self.getSlicesRange = self._saaxisOpts.getSlicesRange
        self.setSlicesRange = self._saaxisOpts.setSlicesRange
        self.sigStartSinogramLoad = self._sinogramViewer.sigSinoLoadStarted
        self.sigEndSinogramLoad = self._sinogramViewer.sigSinoLoadEnded
        self.sigConfigurationChanged = self._saaxisOpts.sigConfigurationChanged

        # expose signals
        self.sigReconstructionSliceChanged = (
            self._saaxisOpts.sigReconstructionSliceChanged
        )
        self.sigAutoCorRequested = self._saaxisOpts.sigAutoCorRequested
        self.sigReconstructionRangeChanged = (
            self._saaxisOpts.sigReconstructionRangeChanged
        )

        # connect signal / slot
        self._sinogramViewer.sigCorEdited.connect(self.setEstimatedAbsoluteCorPosition)
        self._sinogramViewer.sigWidthEdited.connect(self.setDetectionAccuracy)

    def loadSinogram(self):
        """Enforce to load a sinogram with the current settings"""
        self._sinogramViewer.loadSinogram()

    def setScan(self, scan):
        self._sinogramViewer.setScan(scan, update=False)
        self._saaxisOpts.setScan(scan)

    def close(self):
        self._sinogramViewer.close()
        self._sinogramViewer = None
        super().close()


if __name__ == "__main__":
    import tempfile
    import shutil
    from tomwer.core.utils.scanutils import MockHDF5

    app = qt.QApplication([])
    window = SliceAndCorWidget()

    img_width = 216
    slices_folder = tempfile.mkdtemp()

    scan = MockHDF5(
        scan_path=slices_folder,
        n_proj=60,
        n_ini_proj=60,
        create_ini_dark=False,
        create_ini_ref=False,
        dim=img_width,
    ).scan

    window.setScan(scan)
    window.setWindowTitle("cor and slice selection")
    window.show()
    app.exec_()

    shutil.rmtree(slices_folder)
