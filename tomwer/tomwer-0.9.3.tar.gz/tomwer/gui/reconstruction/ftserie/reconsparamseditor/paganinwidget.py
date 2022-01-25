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
__date__ = "10/01/2018"


import logging
from silx.gui import qt
from tomwer.core.process.reconstruction.ftseries.params.paganin import PaganinMode
from tomwer.core.utils.char import BETA_CHAR, DELTA_CHAR
from tomwer.gui.reconstruction.ftserie.h5editor import H5StructEditor
from tomwer.gui.utils.inputwidget import SelectionLineEdit
from tomwer.synctools.ftseries import _QPaganinRP, QReconsParams

logger = logging.getLogger(__name__)


class PaganinWidget(H5StructEditor, qt.QWidget):
    """
    Definition of the tab enabling Paganin reconstruction parameters edition

    :param reconsparams: reconstruction parameters edited by the widget
    """

    def __init__(self, reconsparams, parent=None):
        qt.QWidget.__init__(self, parent=parent)
        H5StructEditor.__init__(self, structID="PAGANIN")
        self._recons_params = None
        self.setReconsParams(recons_params=reconsparams)

        self._groupHideIfNotMulti = []
        # list of widget to hide if the multi mode is not activated
        self._groupHideIfOff = []
        # list of widget to hide if Paganin is off

        self.setLayout(qt.QVBoxLayout())

        self.__buildMode()
        self.__buildUnsharp()
        self.__buildThreshold()
        self.__buildDilate()
        self.__buildMedianMedianFilterSize()
        self.__buidMKeep()

        self.__updatePaganinMode(0)

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        self._makeConnection()

    def setReconsParams(self, recons_params):
        if isinstance(recons_params, QReconsParams):
            _recons_params = recons_params.paganin
        elif isinstance(recons_params, _QPaganinRP):
            _recons_params = recons_params
        else:
            raise ValueError(
                "recons_params should be an instance of QReconsParam or _QPaganinRP"
            )

        if self._recons_params:
            self._recons_params.sigChanged.disconnect(self._update_params)
        self._recons_params = _recons_params
        self.load(self._recons_params)
        self._recons_params.sigChanged.connect(self._update_params)

    def _update_params(self):
        """Update all parameter"""
        self.load(self._recons_params)

    def clear(self):
        pass

    def _makeConnection(self):
        self._qcbpaganin.currentIndexChanged.connect(self._modeChanged)
        self._qleSigmaBeta.editingFinished.connect(self._DBChanged)
        self._qleSigmaBeta2.editingFinished.connect(self._DB2Changed)
        self._unsharp_sigma_coeff.editingFinished.connect(self._unsharpCoeffChanged)
        self._unsharp_sigma_mask_value.editingFinished.connect(
            self._unsharpSigmachanged
        )
        self._qleThreshold.editingFinished.connect(self._thresholdChanged)
        self._qleDilatation.editingFinished.connect(self._dilateChanged)
        self._qleMedianFilterSize.editingFinished.connect(self._medianRChanged)
        self._qcbKeepBone.toggled.connect(self._keepBoneChanged)
        self._qcbKeepSoft.toggled.connect(self._keepSoftChanged)
        self._qcbKeepAbs.toggled.connect(self._keepAbsChanged)
        self._qcbKeepCorr.toggled.connect(self._keepCorrChanged)
        self._qcbKeepMask.toggled.connect(self._keepMaskChanged)

    def __buildMode(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QGridLayout())
        # define paganin combo box
        self._qcbpaganin = qt.QComboBox(self)
        self._qcbpaganin.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        # TODO: use the _paganinRP
        for mode in PaganinMode:
            self._qcbpaganin.addItem(mode.name)
        widget.layout().addWidget(qt.QLabel("Mode", parent=widget), 0, 0)
        widget.layout().addWidget(self._qcbpaganin, 0, 1)
        self._qcbpaganin.currentIndexChanged.connect(self.__updatePaganinMode)
        self.linkComboboxWithH5Variable(self._qcbpaganin, "MODE", fitwithindex=True)

        self._buildAlphaBetaWidgets(widget)
        self.layout().addWidget(widget)
        self._groupHideIfOff.append(self.paganinModeOpt)

    def _buildAlphaBetaWidgets(self, widget):
        self.paganinModeOpt = qt.QWidget(widget)
        self.paganinModeOpt.setLayout(qt.QGridLayout())
        label = DELTA_CHAR + " / " + BETA_CHAR
        self.paganinModeOpt.layout().addWidget(qt.QLabel(label, parent=widget), 1, 0)
        self._qleSigmaBeta = qt.QLineEdit("0", self)
        self.paganinModeOpt.layout().addWidget(self._qleSigmaBeta, 1, 1)
        self.LinkLineEditWithH5Variable(self._qleSigmaBeta, "DB", float)

        label_multi = DELTA_CHAR + " / " + BETA_CHAR + " (multi)"
        lMulti = qt.QLabel(label_multi, parent=widget)
        self.paganinModeOpt.layout().addWidget(lMulti)
        self._qleSigmaBeta2 = qt.QLineEdit("0", self)
        self.paganinModeOpt.layout().addWidget(self._qleSigmaBeta2, 2, 1)
        self.LinkLineEditWithH5Variable(self._qleSigmaBeta2, "DB2", float)
        self._groupHideIfNotMulti.append(lMulti)
        self._groupHideIfNotMulti.append(self._qleSigmaBeta2)

        widget.layout().addWidget(self.paganinModeOpt, 1, 1)

    def _modeChanged(self):
        value = self._qcbpaganin.currentIndex()
        assert isinstance(self._recons_params, _QPaganinRP)
        self._recons_params["MODE"] = value

    def _DBChanged(self):
        value = float(self._qleSigmaBeta.text())
        self._recons_params["DB"] = value

    def _DB2Changed(self):
        value = float(self._qleSigmaBeta2.text())
        self._recons_params["DB2"] = value

    def __buildUnsharp(self):
        # unsharp label
        self._unsharp_group = qt.QGroupBox(title="unsharp mask parameters", parent=self)
        self.layout().addWidget(self._unsharp_group)
        self._unsharp_group.setLayout(qt.QGridLayout())
        label = "mask " + DELTA_CHAR + " value in pixels"
        self._unsharp_group.layout().addWidget(qt.QLabel(label), 0, 0)
        self._unsharp_sigma_coeff = qt.QLineEdit("0", self._unsharp_group)
        self._unsharp_group.layout().addWidget(self._unsharp_sigma_coeff, 0, 1)
        self.LinkLineEditWithH5Variable(
            self._unsharp_sigma_coeff, "UNSHARP_COEFF", float
        )

        self._unsharp_group.layout().addWidget(qt.QLabel("coefficient "), 1, 0)
        self._unsharp_sigma_mask_value = qt.QLineEdit("0", self._unsharp_group)
        validator = qt.QDoubleValidator(parent=self._unsharp_sigma_mask_value)
        self._unsharp_sigma_mask_value.setValidator(validator)
        self._unsharp_group.layout().addWidget(self._unsharp_sigma_mask_value, 1, 1)
        self.LinkLineEditWithH5Variable(
            self._unsharp_sigma_mask_value, "UNSHARP_SIGMA", float
        )

        self.layout().addWidget(self._unsharp_group)
        self._groupHideIfOff.append(self._unsharp_group)

    def _unsharpCoeffChanged(self):
        value = float(self._unsharp_sigma_coeff.text())
        self._recons_params["UNSHARP_COEFF"] = value

    def _unsharpSigmachanged(self):
        value = float(self._unsharp_sigma_mask_value.text())
        self._recons_params["UNSHARP_SIGMA"] = value

    def __buildThreshold(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(
            qt.QLabel("Threshold for high absorption mask", parent=widget)
        )
        self._qleThreshold = qt.QLineEdit("0", widget)
        widget.layout().addWidget(self._qleThreshold)
        self.LinkLineEditWithH5Variable(self._qleThreshold, "THRESHOLD", float)

        self.layout().addWidget(widget)
        self._groupHideIfNotMulti.append(widget)
        self._groupHideIfOff.append(widget)

    def _thresholdChanged(self):
        value = float(self._qleThreshold.text())
        self._recons_params["THRESHOLD"] = value

    def __buildDilate(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(
            qt.QLabel("Dilatation to cover the dark fringes", parent=widget)
        )
        self._qleDilatation = qt.QLineEdit("0", parent=widget)
        widget.layout().addWidget(self._qleDilatation)
        self.LinkLineEditWithH5Variable(self._qleDilatation, "DILATE", int)

        self.layout().addWidget(widget)
        self._groupHideIfNotMulti.append(widget)
        self._groupHideIfOff.append(widget)

    def _dilateChanged(self):
        value = int(self._qleDilatation.text())
        self._recons_params["DILATE"] = value

    def __buildMedianMedianFilterSize(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(qt.QLabel("Median filter size", parent=widget))
        self._qleMedianFilterSize = qt.QLineEdit("", parent=widget)
        widget.layout().addWidget(self._qleMedianFilterSize)
        self.LinkLineEditWithH5Variable(self._qleMedianFilterSize, "MEDIANR", int)

        self.layout().addWidget(widget)
        self._groupHideIfNotMulti.append(widget)
        self._groupHideIfOff.append(widget)

    def _medianRChanged(self):
        value = int(self._qleMedianFilterSize.text())
        self._recons_params["MEDIANR"] = value

    def __buidMKeep(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QVBoxLayout())

        self._qcbKeepBone = qt.QCheckBox(
            "Keep a separate volume for high absorption part", parent=widget
        )
        widget.layout().addWidget(self._qcbKeepBone)
        self.linkCheckboxWithH5Variable(self._qcbKeepBone, "MKEEP_BONE")

        self._qcbKeepSoft = qt.QCheckBox(
            "Keep a separate volume for low absorption part", parent=widget
        )
        widget.layout().addWidget(self._qcbKeepSoft)
        self.linkCheckboxWithH5Variable(self._qcbKeepSoft, "MKEEP_SOFT")

        self._qcbKeepAbs = qt.QCheckBox(
            "Keep a separate volume for absorption reconstruction", parent=widget
        )
        widget.layout().addWidget(self._qcbKeepAbs)
        self.linkCheckboxWithH5Variable(self._qcbKeepAbs, "MKEEP_ABS")

        self._qcbKeepCorr = qt.QCheckBox(
            "Keep binary mask (bone absorption - average neighbours)", parent=widget
        )
        widget.layout().addWidget(self._qcbKeepCorr)
        self.linkCheckboxWithH5Variable(self._qcbKeepCorr, "MKEEP_CORR")

        self._qcbKeepMask = qt.QCheckBox("Keep the binary mask", parent=widget)
        widget.layout().addWidget(self._qcbKeepMask)
        self.linkCheckboxWithH5Variable(self._qcbKeepMask, "MKEEP_MASK")

        self.layout().addWidget(widget)
        self._groupHideIfNotMulti.append(widget)
        self._groupHideIfOff.append(widget)

    def _keepBoneChanged(self, b):
        self._recons_params["MKEEP_BONE"] = b

    def _keepSoftChanged(self, b):
        self._recons_params["MKEEP_SOFT"] = b

    def _keepAbsChanged(self, b):
        self._recons_params["MKEEP_ABS"] = b

    def _keepCorrChanged(self, b):
        self._recons_params["MKEEP_CORR"] = b

    def _keepMaskChanged(self, b):
        self._recons_params["MKEEP_MASK"] = b

    def getPaganinMode(self):
        return self._qcbpaganin.currentText()

    def __updatePaganinMode(self, newindex: int):
        # Deal with PAGANIN node visibility
        [widget.setVisible(newindex != 0) for widget in self._groupHideIfOff]
        [widget.setVisible(newindex == 3) for widget in self._groupHideIfNotMulti]


class PaganinRangeWidget(PaganinWidget):
    def _buildAlphaBetaWidgets(self, widget):
        self.paganinModeOpt = qt.QWidget(widget)
        self.paganinModeOpt.setLayout(qt.QGridLayout())
        label = DELTA_CHAR + " / " + BETA_CHAR
        self.paganinModeOpt.layout().addWidget(qt.QLabel(label, parent=widget), 1, 0)
        self._qleSigmaBeta = SelectionLineEdit(text="0", parent=self)
        self.paganinModeOpt.layout().addWidget(self._qleSigmaBeta, 1, 1)
        self.LinkSelectionLineEditWithH5Variable(self._qleSigmaBeta, "DB", str)

        label_multi = DELTA_CHAR + " / " + BETA_CHAR + " (multi)"
        lMulti = qt.QLabel(label_multi, parent=widget)
        self.paganinModeOpt.layout().addWidget(lMulti)
        self._qleSigmaBeta2 = SelectionLineEdit(text="0", parent=self)
        self.paganinModeOpt.layout().addWidget(self._qleSigmaBeta2, 2, 1)
        self.LinkSelectionLineEditWithH5Variable(self._qleSigmaBeta2, "DB2", str)
        self._groupHideIfNotMulti.append(lMulti)
        self._groupHideIfNotMulti.append(self._qleSigmaBeta2)

        widget.layout().addWidget(self.paganinModeOpt, 1, 1)

    def _DBChanged(self):
        value = self._qleSigmaBeta.selection
        self._recons_params["DB"] = value

    def _DB2Changed(self):
        value = self._qleSigmaBeta2.selection
        self._recons_params["DB2"] = value
