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
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomwer.core.process.reconstruction.darkref.params import When
from tomwer.gui.reconstruction.darkref.darkrefwidget import _WhatCheckBox
from tomwer.gui.reconstruction.ftserie.h5editor import H5StructEditor
from tomwer.synctools.ftseries import QReconsParams, _QDKRFRP

logger = logging.getLogger(__name__)


class DKRFWidget(H5StructEditor, qt.QWidget):
    """
    Group all the variable associated to dark and flat field

     :param : reconstruction parameters edited by the widget
    """

    def __init__(self, reconsparams, parent=None):
        qt.QWidget.__init__(self, parent)
        H5StructEditor.__init__(self, structID="DKRF")
        self._recons_params = None
        self.setReconsParams(recons_params=reconsparams)

        self._updateReconsParam = True

        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.__buildDoWhen())
        self.layout().addWidget(self.__buildDKMode())
        self.layout().addWidget(self.__buildRefMode())
        self.layout().addWidget(self.__buildRm())
        self.layout().addWidget(self.__buildSkip())
        self.layout().addWidget(self.__buildDKPattern())
        self.layout().addWidget(self.__buildRefPattern())

        # spacer
        self.spacer = qt.QWidget(self)
        self.spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(self.spacer)

        self._makeConnection()

    def setReconsParams(self, recons_params):
        if isinstance(recons_params, QReconsParams):
            _recons_params = recons_params.dkrf
        elif isinstance(recons_params, _QDKRFRP):
            _recons_params = recons_params
        else:
            raise ValueError(
                "recons_params should be an instance of QReconsParam or _QDKRFRP"
            )

        if self._recons_params:
            self._recons_params.sigChanged.disconnect(self._update_params)
        self._recons_params = _recons_params
        self.load(self._recons_params)
        self._recons_params.sigChanged.connect(self._update_params)

    def _update_params(self):
        """Update all parameter"""
        self.load(self._recons_params)

    def _makeConnection(self):
        self._qcbRefMode.sigChanged.connect(self._refCalcModeChanged)
        self._qcbDKMode.sigChanged.connect(self._darkCalcModeChanged)
        self._qcbRmRef.toggled.connect(self._rmOptChanged)
        self._qcbSkipRef.toggled.connect(self._skipOptChanged)
        self._qleDKPattern.editingFinished.connect(self._darkPatternChanged)
        self._qleRefsPattern.editingFinished.connect(self._refPatternChanged)

    def __buildDoWhen(self):
        self._doWhenOpt = qt.QWidget(self)
        self._doWhenOpt.setLayout(qt.QHBoxLayout())
        self._doWhenOpt.layout().addWidget(qt.QLabel("when", parent=self._doWhenOpt))
        self._qleDoWhen = qt.QLineEdit("", self._doWhenOpt)
        self._doWhenOpt.layout().addWidget(self._qleDoWhen)
        self.linkGroupWithH5Variable(
            self._qleDoWhen, "DOWHEN", setter=self._setWhen, getter=self._getWhen
        )
        self._doWhenOpt.hide()
        return self._doWhenOpt

    def _setWhen(self, when):
        if isinstance(when, str):
            self._qleDoWhen.setText(when.split(".")[-1])
        elif isinstance(when, When):
            self._qleDoWhen.setText(when.name.split(".")[-1])

    def _getWhen(self):
        return self._qleDoWhen.text()

    def __buildDKMode(self):
        self._qcbDKMode = _WhatCheckBox(parent=self, text="dark")
        self.linkGroupWithH5Variable(
            self._qcbDKMode,
            "DARKCAL",
            getter=self._qcbDKMode.getModeName,
            setter=self._qcbDKMode.setMode,
        )
        return self._qcbDKMode

    def _darkCalcModeChanged(self):
        value = self._qcbDKMode.getMode()
        self._recons_params["DARKCAL"] = value

    def __buildRefMode(self):
        self._qcbRefMode = _WhatCheckBox(parent=self, text="ref")
        self.linkGroupWithH5Variable(
            self._qcbRefMode,
            "REFSCAL",
            getter=self._qcbRefMode.getModeName,
            setter=self._qcbRefMode.setMode,
        )
        return self._qcbRefMode

    def _refCalcModeChanged(self):
        value = self._qcbRefMode.getMode()
        self._recons_params["REFSCAL"] = value

    def __buildRm(self):
        widget = qt.QWidget(parent=self)
        widget.setLayout(qt.QVBoxLayout())
        widget.layout().setContentsMargins(0, 0, 0, 0)
        self._qcbRmRef = qt.QCheckBox("remove", parent=widget)
        widget.layout().addWidget(self._qcbRmRef)
        self.linkCheckboxWithH5Variable(self._qcbRmRef, "REFSRMV")

        self._qcbRmDK = qt.QCheckBox("remove dark", parent=widget)
        self._qcbRmDK.hide()
        self.linkCheckboxWithH5Variable(self._qcbRmDK, "DARKRMV")
        widget.layout().addWidget(self._qcbRmDK)

        return widget

    def _rmOptChanged(self, b):
        self._recons_params["REFSRMV"] = b
        self._recons_params["DARKRMV"] = b

    def __buildSkip(self):
        widget = qt.QWidget(parent=self)
        widget.setLayout(qt.QVBoxLayout())
        widget.layout().setContentsMargins(0, 0, 0, 0)
        self._qcbSkipRef = qt.QCheckBox("skip", parent=widget)
        widget.layout().addWidget(self._qcbSkipRef)
        self.linkCheckboxWithH5Variable(self._qcbSkipRef, "REFSOVE", invert=True)

        self._qcbSkipDK = qt.QCheckBox("skip dark", parent=widget)
        self._qcbSkipDK.hide()
        self.linkCheckboxWithH5Variable(self._qcbSkipDK, "DARKOVE", invert=True)
        widget.layout().addWidget(self._qcbSkipDK)

        return widget

    def _skipOptChanged(self, b):
        # The interface control both REFSRMV and DARKRMV
        self._recons_params._set_skip_if_exist(b)

    def __buildDKPattern(self):
        self._DKPatternOpt = qt.QWidget(self)
        self._DKPatternOpt.setLayout(qt.QHBoxLayout())
        self._DKPatternOpt.layout().addWidget(
            qt.QLabel("dark file pattern", parent=self._DKPatternOpt)
        )
        self._qleDKPattern = qt.QLineEdit("", self._DKPatternOpt)
        self._DKPatternOpt.layout().addWidget(self._qleDKPattern)
        self.LinkLineEditWithH5Variable(self._qleDKPattern, "DKFILE", str)
        self._qleDKPattern.setToolTip(DarkRefs.getDarkPatternTooltip())
        return self._DKPatternOpt

    def _darkPatternChanged(self):
        value = self._qleDKPattern.text()
        self._recons_params["DKFILE"] = value

    def __buildRefPattern(self):
        self._RefsPatternOpt = qt.QWidget(self)
        self._RefsPatternOpt.setLayout(qt.QHBoxLayout())
        self._RefsPatternOpt.layout().addWidget(
            qt.QLabel("refs file pattern", parent=self._RefsPatternOpt)
        )
        self._qleRefsPattern = qt.QLineEdit("", self._RefsPatternOpt)
        self._RefsPatternOpt.layout().addWidget(self._qleRefsPattern)
        self.LinkLineEditWithH5Variable(self._qleRefsPattern, "RFFILE", str)
        self._qleRefsPattern.setToolTip(DarkRefs.getRefPatternTooltip())
        return self._RefsPatternOpt

    def _refPatternChanged(self):
        value = self._qleRefsPattern.text()
        self._recons_params["RFFILE"] = value
