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
__date__ = "11/02/2020"


import typing
from tomwer.utils import docstring
from silx.gui import qt
from tomwer.gui.utils.scrollarea import QComboBoxIgnoreWheel as QComboBox
from tomwer.gui.reconstruction.nabu.nabuconfig import base
from tomwer.gui.utils.inputwidget import SelectionLineEdit
from tomwer.core.utils.char import BETA_CHAR, DELTA_CHAR
from tomwer.core.process.reconstruction.nabu.utils import _NabuStages, _NabuPhaseMethod
import logging
from silx.utils.enum import Enum as _Enum

_logger = logging.getLogger(__name__)


class PaddingMode(_Enum):
    ZEROS = "zeros"
    MEAN = "mean"
    EDGE = "edge"
    SYMMETRIC = "symmetric"
    REFLECT = "reflect"


# assert set(PaddingMode.values()) == set(PaganinPhaseRetrieval.available_padding_modes)
#


class _NabuPhaseConfig(qt.QWidget, base._NabuStageConfigBase):
    """
    Widget to define the configuration of the nabu preprocessing
    """

    sigConfChanged = qt.Signal(str)
    """Signal emitted when the configuration change. Parameter is the option
    modified
    """

    def __init__(self, parent, scrollArea):
        qt.QWidget.__init__(self, parent, stage=_NabuStages.PHASE)
        base._NabuStageConfigBase.__init__(self, stage=_NabuStages.PHASE)
        self.setLayout(qt.QGridLayout())

        # phase method
        self._methodLabel = qt.QLabel("method", self)
        self.layout().addWidget(self._methodLabel, 1, 0, 1, 1)
        self._methodCB = QComboBox(parent=self, scrollArea=scrollArea)
        for method in _NabuPhaseMethod:
            self._methodCB.addItem(method.value)
        self.layout().addWidget(self._methodCB, 1, 1, 1, 3)
        self.registerWidget(self._methodLabel, "required")
        self.registerWidget(self._methodCB, "required")

        # paganin options
        self._paganinOpts = NabuPaganinConfig(parent=self, scrollArea=scrollArea)
        self.layout().addWidget(self._paganinOpts, 2, 0, 3, 3)

        # unsharp options
        self._unsharpOpts = NabuUnsharpConfig(parent=self)
        self.layout().addWidget(self._unsharpOpts, 6, 0, 3, 3)

        # spacer for style
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer, 200, 1, 1, 1)

        # set up
        item_index = self._methodCB.findText(_NabuPhaseMethod.PAGANIN.value)
        assert item_index >= 0
        self._methodCB.setCurrentIndex(item_index)

        # connect signal / slot
        self._methodCB.currentIndexChanged.connect(self._methodChanged)
        self._paganinOpts.sigConfChanged.connect(self._signalConfChanged)
        self._unsharpOpts.sigConfChanged.connect(self._signalConfChanged)

        # set up
        self._paganinOpts.setEnabled(self.getMethod() is not _NabuPhaseMethod.NONE)

    def _methodChanged(self, *args, **kwargs):
        self._paganinOpts.setEnabled(self.getMethod() is not _NabuPhaseMethod.NONE)
        self._signalConfChanged("method")

    def _signalConfChanged(self, param):
        self.sigConfChanged.emit(param)

    def getMethod(self) -> _NabuPhaseMethod:
        return _NabuPhaseMethod.from_value(self._methodCB.currentText())

    @docstring(base._NabuStageConfigBase)
    def setConfiguration(self, config) -> None:
        if "method" in config:
            method = config.get("method", _NabuPhaseMethod.NONE)
            if method == "none":
                method = _NabuPhaseMethod.NONE
            self._paganinOpts.setConfiguration(config)
            method = _NabuPhaseMethod.from_value(method)
            index_method = self._methodCB.findText(method.value)
            if index_method >= 0:
                self._methodCB.setCurrentIndex(index_method)
            else:
                _logger.warning("unable to find method {method}")
        self._unsharpOpts.setConfiguration(config)

    @docstring(base._NabuStageConfigBase)
    def getConfiguration(self) -> dict:
        configuration = {"method": self.getMethod().value}
        if self.getMethod() is _NabuPhaseMethod.PAGANIN:
            configuration.update(self._paganinOpts.getConfiguration())
        configuration.update(self._unsharpOpts.getConfiguration())
        return configuration

    def setConfigurationLevel(self, level):
        base._NabuStageConfigBase.setConfigurationLevel(self, level)
        self._unsharpOpts.setConfigurationLevel(level=level)
        self._paganinOpts.setConfigurationLevel(level=level)

    def setDeltaBetaValue(self, value):
        self._paganinOpts.setDeltaBetaValue(value)


class NabuPaganinConfig(qt.QWidget, base._NabuStageConfigBase):
    """Configuration widget dedicated to the paganin options for nabu"""

    sigConfChanged = qt.Signal(str)
    """Signal emitted when the configuration change. Parameter is the option
    modified
    """

    def __init__(self, parent, scrollArea):
        qt.QWidget.__init__(self, parent=parent, stage=_NabuStages.PHASE)
        base._NabuStageConfigBase.__init__(self, stage=_NabuStages.PHASE)
        self.setLayout(qt.QGridLayout())

        # paganin delta / beta
        label = DELTA_CHAR + " / " + BETA_CHAR
        self._db_label = qt.QLabel(label, self)
        self.layout().addWidget(self._db_label, 0, 0, 1, 1)
        self._deltaBetaQLE = SelectionLineEdit("100.0", self)
        self.layout().addWidget(self._deltaBetaQLE, 0, 1, 1, 3)
        self.registerWidget(self._db_label, "required")
        self.registerWidget(self._deltaBetaQLE, "required")

        # paganin lmicron
        # we skip this paramter, only used for compatibility

        # paganin margin
        # note: hide for now margin as it is not connected at nabu side
        # self.layout().addWidget(qt.QLabel("margin"), 1, 0, 1, 1)
        # self._margeQSB = qt.QSpinBox(self)
        # self._margeQSB.setMinimum(0)
        # self._margeQSB.setMaximum(9999)
        # self._margeQSB.setToolTip(
        #     "Marge (in pixels) in the Paganin filtering "
        #     "to avoid local tomography artefacts"
        # )
        # self.layout().addWidget(self._margeQSB, 1, 1, 1, 1)
        # self.registerWidget(self._margeQSB, "optional")

        # paganin padding_type
        self._paddingLabel = qt.QLabel("padding", self)
        self.layout().addWidget(self._paddingLabel, 2, 0, 1, 1)
        self._paddingTypeCB = QComboBox(self, scrollArea=scrollArea)
        self._paddingTypeCB.setToolTip(
            "Padding type for the filtering step " "in Paganin/CTR."
        )
        for padding_type in (PaddingMode.ZEROS, PaddingMode.ZEROS.EDGE):
            self._paddingTypeCB.addItem(padding_type.value)
        self.layout().addWidget(self._paddingTypeCB, 2, 1, 1, 3)
        self.registerWidget(self._paddingLabel, "advanced")
        self.registerWidget(self._paddingTypeCB, "advanced")

        # set up
        # note: hide for now margin as it is not connected at nabu side
        # self._margeQSB.setValue(50)
        item_index = self._paddingTypeCB.findText(PaddingMode.EDGE.value)
        self._paddingTypeCB.setCurrentIndex(item_index)

        # connect signal - slot
        self._deltaBetaQLE.editingFinished.connect(self._paganinDBChanged)
        # note: hide for now margin as it is not connected at nabu side
        # self._margeQSB.editingFinished.connect(self._paganinMargeChanged)
        self._paddingTypeCB.currentIndexChanged.connect(self._paganinPaddingTypeChanged)

    def _paganinDBChanged(self, *args, **kwargs):
        self._signalConfChanged("delta_beta")

    def _paganinMargeChanged(self, *args, **kwargs):
        self._signalConfChanged("marge")

    def _paganinPaddingTypeChanged(self, *args, **kwargs):
        self._signalConfChanged("padding_type")

    def getPaddingType(self) -> PaddingMode:
        current_text = self._paddingTypeCB.currentText()
        return PaddingMode.from_value(current_text)

    # note: hide for now margin as it is not connected at nabu side
    # def getMarge(self) -> int:
    #     return int(self._margeQSB.text())

    def getDeltaBeta(self) -> str:
        return self._deltaBetaQLE.text()

    def setDeltaBetaValue(self, value):
        self._deltaBetaQLE.setText(str(value))

    def getConfiguration(self):
        return {
            "delta_beta": self.getDeltaBeta(),  # this one is not cast because can contain several values
            # "margin": self.getMarge(),
            "padding_type": self.getPaddingType().value,
        }

    def setConfiguration(self, conf):
        if "delta_beta" in conf:
            self._deltaBetaQLE.setText(str(conf["delta_beta"]))
        # if "margin" in conf:
        #     self._margeQSB.setValue(int(conf["margin"]))
        if "padding_type" in conf:
            padding_type = PaddingMode.from_value(conf["padding_type"])
            item_index = self._paddingTypeCB.findText(padding_type.value)
            self._paddingTypeCB.setCurrentIndex(item_index)

    def _signalConfChanged(self, param):
        self.sigConfChanged.emit(param)


class NabuUnsharpConfig(qt.QWidget, base._NabuStageConfigBase):
    """Configuration widget dedicated to the unsharp options for nabu"""

    sigConfChanged = qt.Signal(str)
    """Signal emitted when the configuration change. Parameter is the option
    modified
    """

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent, stage=_NabuStages.PHASE)
        base._NabuStageConfigBase.__init__(self, stage=_NabuStages.PHASE)
        self.setLayout(qt.QGridLayout())

        # unsharp coeff
        self._unsharpCoeffCB = qt.QCheckBox("unsharp coeff", self)
        self._unsharpCoeffCB.setToolTip(
            "Unsharp mask strength. The unsharped "
            "image is equal to\n  UnsharpedImage "
            "=  (1 + coeff)*originalPaganinImage "
            "- coeff * ConvolvedImage. Setting "
            "this coefficient to zero means that "
            "no unsharp mask will be applied."
        )
        self.layout().addWidget(self._unsharpCoeffCB, 0, 0, 1, 1)
        self._unsharpCoeffQLE = qt.QLineEdit("", self)
        self._unsharpCoeffQLE.setValidator(qt.QDoubleValidator())
        self.layout().addWidget(self._unsharpCoeffQLE, 0, 1, 1, 1)
        self.registerWidget(self._unsharpCoeffCB, "optional")
        self._unsharpCoeffOpt = self.registerWidget(self._unsharpCoeffQLE, "optional")

        # unsharp_sigma
        self._unsharpSigmaCB = qt.QCheckBox("unsharp sigma", self)
        self._unsharpSigmaCB.setToolTip(
            "Standard deviation of the Gaussian "
            "filter when applying an unsharp "
            "mask\nafter the Paganin filtering. "
            "Disabled if set to 0."
        )
        self.layout().addWidget(self._unsharpSigmaCB, 1, 0, 1, 1)
        self._unsharpSigmaQLE = qt.QLineEdit("", self)
        self._unsharpSigmaQLE.setValidator(qt.QDoubleValidator())
        self.layout().addWidget(self._unsharpSigmaQLE, 1, 1, 1, 1)
        self.registerWidget(self._unsharpSigmaCB, "optional")
        self._unsharpSigmaOpt = self.registerWidget(self._unsharpSigmaQLE, "optional")

        # set up
        self._unsharpCoeffCB.setChecked(False)
        self._unsharpCoeffQLE.setText(str(3.0))
        self._unsharpSigmaCB.setChecked(False)
        self._unsharpSigmaQLE.setText(str(0.8))
        self._showUnsharpCoeffQLE(False)
        self._showUnsharpSigmaQLE(False)

        # signal / slot connection
        ## unsharp coeff
        self._unsharpCoeffCB.toggled.connect(self._showUnsharpCoeffQLE)
        self._unsharpCoeffCB.toggled.connect(self._unsharpCoeffChanged)
        self._unsharpCoeffQLE.editingFinished.connect(self._unsharpCoeffChanged)
        ## unsharp sigma
        self._unsharpSigmaCB.toggled.connect(self._showUnsharpSigmaQLE)
        self._unsharpSigmaCB.toggled.connect(self._unsharpSigmaChanged)
        self._unsharpSigmaQLE.editingFinished.connect(self._unsharpSigmaChanged)

    def _unsharpCoeffChanged(self, *args, **kwargs):
        self._signalConfChanged("unsharp_coeff")

    def _unsharpSigmaChanged(self, *args, **kwargs):
        self._signalConfChanged("unsharp_sigma")

    def isUnsharpCoeffActive(self):
        return self._unsharpCoeffCB.isChecked()

    def isUnsharpSigmaActive(self):
        return self._unsharpSigmaCB.isChecked()

    def _showUnsharpCoeffQLE(self, visible):
        self._unsharpCoeffOpt.setVisible(visible)

    def _showUnsharpSigmaQLE(self, visible):
        self._unsharpSigmaOpt.setVisible(visible)

    def _signalConfChanged(self, param):
        self.sigConfChanged.emit(param)

    def getUnsharpCoeff(self) -> typing.Union[float, int]:
        if self.isUnsharpCoeffActive():
            return float(self._unsharpCoeffQLE.text())
        else:
            return 0

    def setUnsharpCoeff(self, coeff):
        if coeff == 0.0:
            self._unsharpCoeffCB.setChecked(False)
        else:
            self._unsharpCoeffCB.setChecked(True)
            self._unsharpCoeffQLE.setText(str(coeff))

    def getUnsharpSigma(self) -> typing.Union[float, int]:
        if self.isUnsharpSigmaActive():
            return float(self._unsharpSigmaQLE.text())
        else:
            return 0

    def setUnsharpSigma(self, sigma):
        if sigma == 0.0:
            self._unsharpSigmaCB.setChecked(False)
        else:
            self._unsharpSigmaCB.setChecked(True)
            self._unsharpSigmaQLE.setText(str(sigma))

    def getConfiguration(self):
        return {
            "unsharp_coeff": self.getUnsharpCoeff(),
            "unsharp_sigma": self.getUnsharpSigma(),
        }

    def setConfiguration(self, conf):
        if "unsharp_coeff" in conf:
            self.setUnsharpCoeff(float(conf["unsharp_coeff"]))
        if "unsharp_sigma" in conf:
            self.setUnsharpSigma(float(conf["unsharp_sigma"]))
