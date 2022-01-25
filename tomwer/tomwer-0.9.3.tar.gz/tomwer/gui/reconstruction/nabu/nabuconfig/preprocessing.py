# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
__date__ = "06/12/2021"


from silx.gui import qt
from tomwer.gui.reconstruction.nabu.nabuconfig.base import _NabuStageConfigBase
from tomwer.utils import docstring
from tomwer.core.process.reconstruction.nabu.utils import (
    _NabuStages,
    _RingCorrectionMethod,
)
from tomwer.gui.utils.scrollarea import QDoubleSpinBoxIgnoreWheel as QDoubleSpinBox
import logging

_logger = logging.getLogger(__name__)


class _NabuPreProcessingConfig(_NabuStageConfigBase, qt.QWidget):
    """
    Widget to define the configuration of the nabu preprocessing
    """

    sigConfChanged = qt.Signal(str)
    """Signal emitted when the configuration change. Parameter is the option
    modified
    """

    def __init__(self, parent, scrollArea):
        _NabuStageConfigBase.__init__(self, stage=_NabuStages.PRE)
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QGridLayout())

        # flat field
        self._flatFieldCB = qt.QCheckBox("flat field correction", self)
        self._flatFieldCB.setToolTip("Whether to enable flat-field " "normalization")
        self.layout().addWidget(self._flatFieldCB, 0, 0, 1, 2)
        self.registerWidget(self._flatFieldCB, "optional")

        # double flat field
        self._dffCB = qt.QCheckBox("double flat field correction", self)
        self._dffCB.setToolTip("Whether to enable double flat field " "normalization")
        self.layout().addWidget(self._dffCB, 1, 0, 1, 2)
        self._dffSigmaLabel = qt.QLabel("sigma:", self)
        self._dffSigmaLabel.setAlignment(qt.Qt.AlignRight)
        self.layout().addWidget(self._dffSigmaLabel, 1, 2, 1, 1)
        self._dffSigmaQDSB = QDoubleSpinBox(parent=self, scrollArea=scrollArea)
        self._dffSigmaQDSB.setMinimum(0.0)
        self._dffSigmaQDSB.setDecimals(2)
        self._dffSigmaQDSB.setSingleStep(0.1)
        self.layout().addWidget(self._dffSigmaQDSB, 1, 3, 1, 1)
        self.registerWidget(self._flatFieldCB, "required")
        self._dffOptWidgets = [
            self.registerWidget(self._dffSigmaLabel, "required"),
            self.registerWidget(self._dffSigmaQDSB, "required"),
        ]

        # sino ring corrcetion
        self._sinoRingCorrectionCB = qt.QLabel("rings removal method", self)
        self._sinoRingCorrectionCB.setToolTip("Sinogram rings removal method")
        self.layout().addWidget(self._sinoRingCorrectionCB, 2, 0, 1, 2)
        self.registerWidget(self._sinoRingCorrectionCB, "required")

        self._sinoRingCorrectionMthd = qt.QComboBox(self)
        for method in _RingCorrectionMethod:
            self._sinoRingCorrectionMthd.addItem(method.value)
        self.layout().addWidget(self._sinoRingCorrectionMthd, 2, 2, 1, 1)
        self.registerWidget(self._sinoRingCorrectionMthd, "required")

        # ccd filter
        self._ccdFilterCB = qt.QCheckBox("CCD hot spot correction", self)
        self._ccdFilterCB.setToolTip("Whether to enable the CCD hotspots " "correction")
        self.layout().addWidget(self._ccdFilterCB, 4, 0, 1, 2)
        self.registerWidget(self._ccdFilterCB, "optional")

        # ccd filter threshold
        self._ccdHotspotLabel = qt.QLabel("threshold:", self)
        self._ccdHotspotLabel.setAlignment(qt.Qt.AlignRight)
        self.layout().addWidget(self._ccdHotspotLabel, 5, 2, 1, 1)
        self._ccdThreshold = QDoubleSpinBox(self, scrollArea)
        self._ccdThreshold.setMinimum(0.0)
        self._ccdThreshold.setMaximum(999999)
        self._ccdThreshold.setSingleStep(0.01)
        self._ccdThreshold.setDecimals(6)
        tooltip = (
            "If ccd_filter_enabled = 1, a median filter is applied on "
            "the 3X3 neighborhood\nof every pixel. If a pixel value "
            "exceeds the median value more than this parameter,\nthen "
            "the pixel value is replaced with the median value."
        )
        self._ccdThreshold.setToolTip(tooltip)
        self.layout().addWidget(self._ccdThreshold, 5, 3, 1, 1)
        self._ccdOptWidgets = [
            self.registerWidget(self._ccdHotspotLabel, "optional"),
            self.registerWidget(self._ccdThreshold, "optional"),
        ]

        # take logarithm
        self._takeLogarithmCB = qt.QCheckBox("take logarithm", self)
        self.layout().addWidget(self._takeLogarithmCB, 6, 0, 1, 2)
        self.registerWidget(self._takeLogarithmCB, "required")

        # log min clip value
        self._clipMinLogValueLabel = qt.QLabel("log min clip value:", self)
        self._clipMinLogValueLabel.setAlignment(qt.Qt.AlignRight)
        self.layout().addWidget(self._clipMinLogValueLabel, 7, 2, 1, 1)
        self._clipMinLogValue = QDoubleSpinBox(self, scrollArea=scrollArea)
        self._clipMinLogValue.setMinimum(0.0)
        self._clipMinLogValue.setMaximum(9999999)
        self._clipMinLogValue.setSingleStep(0.01)
        self._clipMinLogValue.setDecimals(6)
        self.layout().addWidget(self._clipMinLogValue, 7, 3, 1, 1)
        self._takeLogOpt = [
            self.registerWidget(self._clipMinLogValueLabel, "optional"),
            self.registerWidget(self._clipMinLogValue, "optional"),
        ]

        # log max clip value
        self._clipMaxLogValueLabel = qt.QLabel("log max clip value:", self)
        self._clipMaxLogValueLabel.setAlignment(qt.Qt.AlignRight)
        self.layout().addWidget(self._clipMaxLogValueLabel, 8, 2, 1, 1)
        self._clipMaxLogValue = QDoubleSpinBox(self, scrollArea=scrollArea)
        self._clipMaxLogValue.setMinimum(0.0)
        self._clipMaxLogValue.setMaximum(9999999)
        self._clipMaxLogValue.setSingleStep(0.01)
        self._clipMaxLogValue.setDecimals(6)
        self.layout().addWidget(self._clipMaxLogValue, 8, 3, 1, 1)
        self._takeLogOpt.extend(
            [
                self.registerWidget(self._clipMaxLogValueLabel, "optional"),
                self.registerWidget(self._clipMaxLogValue, "optional"),
            ]
        )

        # spacer for style
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 99, 0, 1, 1)

        # set up
        self._flatFieldCB.setChecked(True)
        self.setDFFOptVisible(False)

        self._ccdFilterCB.setChecked(False)
        self._ccdThreshold.setValue(0.04)

        self._clipMinLogValue.setValue(1e-6)
        self._clipMaxLogValue.setValue(10.0)
        self._takeLogarithmCB.setChecked(True)
        self.setCCDOptsVisible(False)

        # connect signal / slot
        self._ccdFilterCB.toggled.connect(self.setCCDOptsVisible)
        self._takeLogarithmCB.toggled.connect(self.setLogClipValueVisible)
        self._flatFieldCB.toggled.connect(self._flatFieldChanged)
        self._dffCB.toggled.connect(self._dffChanged)
        self._dffCB.toggled.connect(self.setDFFOptVisible)
        self._dffSigmaQDSB.valueChanged.connect(self._dffSigmaChanged)
        self._ccdFilterCB.toggled.connect(self._ccdFilterChanged)
        self._ccdThreshold.editingFinished.connect(self._ccdFilterThresholdChanged)
        self._clipMinLogValue.editingFinished.connect(self._logMinClipChanged)
        self._clipMaxLogValue.editingFinished.connect(self._logMaxClipChanged)
        self._takeLogarithmCB.toggled.connect(self._takeLogarithmChanged)
        self._sinoRingCorrectionMthd.currentIndexChanged.connect(
            self._sinoRingCorrectionChanged
        )

    def _flatFieldChanged(self, *args, **kwargs):
        self._signalConfChanged("flatfield_enabled")

    def _dffChanged(self, *args, **kwargs):
        self._signalConfChanged("double_flatfield_enabled")

    def _dffSigmaChanged(self, *args, **kwargs):
        self._signalConfChanged("dff_sigma")

    def _ccdFilterChanged(self, *args, **kwargs):
        self._signalConfChanged("ccd_filter_enabled")

    def _ccdFilterThresholdChanged(self, *args, **kwargs):
        self._signalConfChanged("ccd_filter_threshold")

    def _logMinClipChanged(self, *args, **kwargs):
        self._signalConfChanged("log_min_clip")

    def _logMaxClipChanged(self, *args, **kwargs):
        self._signalConfChanged("log_max_clip")

    def _takeLogarithmChanged(self, *args, **kwargs):
        self._signalConfChanged("take_logarithm")

    def _sinoRingCorrectionChanged(self, *args, **kwargs):
        self._signalConfChanged("sino_rings_correction")

    def _signalConfChanged(self, param, *args, **kwargs):
        self.sigConfChanged.emit(param)

    def setDFFOptVisible(self, visible):
        for widget in self._dffOptWidgets:
            widget.setVisible(visible)

    def setCCDOptsVisible(self, visible):
        for widget in self._ccdOptWidgets:
            widget.setVisible(visible)

    def setLogClipValueVisible(self, visible):
        for widget in self._takeLogOpt:
            widget.setVisible(visible)

    def isFlatFieldActivate(self):
        return self._flatFieldCB.isChecked()

    def isDoubleFlatFieldActivate(self):
        return self._dffCB.isChecked()

    def getDFFSigma(self) -> float:
        """

        :return: double flat field sigma
        """
        return self._dffSigmaQDSB.value()

    def isCCDFilterActivate(self):
        return self._ccdFilterCB.isChecked()

    def getCCDThreshold(self) -> float:
        return float(self._ccdThreshold.text())

    def getLogMinClipValue(self) -> float:
        return float(self._clipMinLogValue.text())

    def getLogMaxClipValue(self) -> float:
        return float(self._clipMaxLogValue.text())

    def getTakeLogarithm(self):
        return self._takeLogarithmCB.isChecked()

    def getSinoRingcorrectionMethod(self) -> str:
        return self._sinoRingCorrectionMthd.currentText()

    @docstring(_NabuStageConfigBase)
    def getConfiguration(self):
        return {
            "flatfield_enabled": int(self.isFlatFieldActivate()),
            "double_flatfield_enabled": int(self.isDoubleFlatFieldActivate()),
            "dff_sigma": self.getDFFSigma(),
            "ccd_filter_enabled": int(self.isCCDFilterActivate()),
            "ccd_filter_threshold": self.getCCDThreshold(),
            "take_logarithm": self.getTakeLogarithm(),
            "log_min_clip": self.getLogMinClipValue(),
            "log_max_clip": self.getLogMaxClipValue(),
            "sino_rings_correction": self.getSinoRingcorrectionMethod(),
        }

    @docstring(_NabuStageConfigBase)
    def setConfiguration(self, conf):
        try:
            self._setConfiguration(conf)
        except Exception as e:
            _logger.error(e)

    def _setConfiguration(self, conf):
        if "flatfield_enabled" in conf:
            ff = conf["flatfield_enabled"]
            if ff is not None:
                self._flatFieldCB.setChecked(bool(ff))
        if "double_flatfield_enabled" in conf:
            dff = conf["double_flatfield_enabled"]
            if dff is not None:
                self._dffCB.setChecked(bool(dff))
        if "dff_sigma" in conf:
            dff_sigma = conf["dff_sigma"]
            if dff_sigma not in (None, "", "none"):
                self._dffSigmaQDSB.setValue(float(dff_sigma))
        if "ccd_filter_enabled" in conf:
            ccd_filter = conf["ccd_filter_enabled"]
            if ccd_filter not in (None, "", "none"):
                self._ccdFilterCB.setChecked(bool(ccd_filter))
        if "ccd_filter_threshold" in conf:
            ccd_filter_threshold = conf["ccd_filter_threshold"]
            if ccd_filter_threshold not in (None, "", "none"):
                self._ccdThreshold.setValue(float(ccd_filter_threshold))
        if "take_logarithm" in conf:
            take_logarithm = conf["take_logarithm"]
            if take_logarithm not in (None, "", "none"):
                self._takeLogarithmCB.setChecked(bool(take_logarithm))
        if "log_min_clip" in conf:
            clip_value = conf["log_min_clip"]
            if clip_value not in (None, "", "none"):
                self._clipMinLogValue.setValue(float(clip_value))
        if "log_max_clip" in conf:
            clip_value = conf["log_max_clip"]
            if clip_value not in (None, "", "none"):
                self._clipMaxLogValue.setValue(float(clip_value))
        sino_rings_correction = conf.get("sino_rings_correction", None)
        if sino_rings_correction is not None:
            if sino_rings_correction == "":
                sino_rings_correction = _RingCorrectionMethod.NONE
            sino_rings_correction = _RingCorrectionMethod.from_value(
                sino_rings_correction
            ).value
            idx = self._sinoRingCorrectionMthd.findText(sino_rings_correction)
            if idx >= 0:
                self._sinoRingCorrectionMthd.setCurrentIndex(idx)
