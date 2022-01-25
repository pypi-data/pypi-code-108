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
from tomwer.gui.reconstruction.ftserie.h5editor import H5StructEditor
from tomwer.synctools.ftseries import QReconsParams, _QBeamGeoRP

logger = logging.getLogger(__name__)


class BeamGeoWidget(H5StructEditor, qt.QWidget):
    """
    Definition of the PyHST tab to edit the Geometry parameters

    :param reconsparams: reconstruction parameters edited by the widget
    """

    def __init__(self, parent=None, reconsparams=None):
        qt.QWidget.__init__(self, parent)
        H5StructEditor.__init__(self, structID="BEAMGEO")
        self._recons_params = None
        self.setReconsParams(recons_params=reconsparams)

        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.__buildType())
        self.layout().addWidget(self.__buildSXSYDist())

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # set up
        self._geometryChanged()
        # connect signal / slot
        self._makeConnection()

    def setReconsParams(self, recons_params):
        if isinstance(recons_params, QReconsParams):
            _recons_params = recons_params.beam_geo
        elif isinstance(recons_params, _QBeamGeoRP):
            _recons_params = recons_params
        else:
            raise ValueError(
                "recons_params should be an instance of QReconsParam or _QBeamGeoRP"
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
        self._qcbType.currentIndexChanged.connect(self._typeChanged)
        self._qleSX.editingFinished.connect(self._SXChanged)
        self._qleSY.editingFinished.connect(self._SYChanged)
        self._qleDIST.editingFinished.connect(self._distChanged)
        self._qcbType.currentIndexChanged.connect(self._geometryChanged)

    def __buildType(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())
        # add QLabel
        widget.layout().addWidget(qt.QLabel("Reconstruction geometry :", widget))
        # build combobox
        self._qcbType = qt.QComboBox(widget)
        self.dic = {"parallel": "p", "conical": "c", "fan beam": "f"}
        for key in self.dic.keys():
            self._qcbType.addItem(key)
        self.linkComboboxWithH5Variable(self._qcbType, "TYPE", dic=self.dic)
        widget.layout().addWidget(self._qcbType)

        return widget

    def _typeChanged(self):
        if self._isLoading is False:
            value = self.dic[self._qcbType.currentText()]
            self._recons_params._set_parameter_value(parameter="TYPE", value=value)

    def __buildSXSYDist(self):
        self._geoOptsWidget = qt.QWidget(self)
        self._geoOptsWidget.setLayout(qt.QGridLayout())

        # SX
        self._qleSX = qt.QLineEdit("", parent=self._geoOptsWidget)
        self.LinkLineEditWithH5Variable(self._qleSX, "SX", float)
        validator = qt.QDoubleValidator(parent=self._qleSX)
        self._qleSX.setValidator(validator)
        self._geoOptsWidget.layout().addWidget(self._qleSX, 0, 1)
        self._geoOptsWidget.layout().addWidget(
            qt.QLabel(
                "Source position on vertical axis X (mm)", parent=self._geoOptsWidget
            ),
            0,
            0,
        )

        # SY
        self._qleSY = qt.QLineEdit("", parent=self._geoOptsWidget)
        self.LinkLineEditWithH5Variable(self._qleSY, "SY", float)
        validator = qt.QDoubleValidator(parent=self._qleSY)
        self._qleSY.setValidator(validator)
        self._geoOptsWidget.layout().addWidget(self._qleSY, 1, 1)
        self._geoOptsWidget.layout().addWidget(
            qt.QLabel(
                "Source position on vertical axis Y (mm)", parent=self._geoOptsWidget
            ),
            1,
            0,
        )

        # DIST
        self._qleDIST = qt.QLineEdit("", parent=self._geoOptsWidget)
        self.LinkLineEditWithH5Variable(self._qleDIST, "DIST", float)
        validator = qt.QDoubleValidator(parent=self._qleDIST)
        self._qleDIST.setValidator(validator)
        self._geoOptsWidget.layout().addWidget(self._qleDIST, 2, 1)
        self._geoOptsWidget.layout().addWidget(
            qt.QLabel("Source distance (m)", parent=self._geoOptsWidget), 2, 0
        )

        return self._geoOptsWidget

    def _SXChanged(self):
        if self._isLoading is False:
            value = float(self._qleSX.text())
            self._recons_params._set_parameter_value(parameter="SX", value=value)

    def _SYChanged(self):
        if self._isLoading is False:
            value = float(self._qleSY.text())
            self._recons_params._set_parameter_value(parameter="SY", value=value)

    def _distChanged(self):
        if self._isLoading is False:
            value = float(self._qleDIST.text())
            self._recons_params._set_parameter_value(parameter="DIST", value=value)

    def _geometryChanged(self, *args, **kwargs):
        self._geoOptsWidget.setVisible(self._qcbType.currentText() != "parallel")
