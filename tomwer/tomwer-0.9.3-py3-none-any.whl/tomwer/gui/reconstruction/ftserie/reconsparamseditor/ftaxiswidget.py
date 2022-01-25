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


from silx.gui import qt
import logging
from tomoscan.scanbase import _FOV
from tomwer.synctools.ftseries import QReconsParams
from tomwer.gui.reconstruction.ftserie.h5editor.h5structseditor import H5StructsEditor

logger = logging.getLogger(__name__)


class FTAxisWidget(H5StructsEditor, qt.QWidget):
    """
    Widget containing all the information to edit the AXIS parameters

    :param reconsparams: reconstruction parameters edited by the widget
    """

    def __init__(self, reconsparams, parent=None):
        qt.QWidget.__init__(self, parent)
        H5StructsEditor.__init__(self, structsManaged=("FT", "FTAXIS"))

        assert isinstance(reconsparams, QReconsParams)

        self._recons_params = None
        self.setReconsParams(recons_params=reconsparams)

        # build gui
        self.setLayout(qt.QVBoxLayout())

        self._qcbHalfAcq = qt.QCheckBox("Half acquisition (HA)", parent=self)
        self.layout().addWidget(self._qcbHalfAcq)

        self._doAxisCorrection = qt.QCheckBox("apply axis correction", parent=self)
        self._doAxisCorrection.setToolTip(
            "If activated then ask to pyhst to " "do axis translation correction"
        )
        self.layout().addWidget(self._doAxisCorrection)
        # for now the axis correction (one value per projection - when detector
        # moves is not managed)
        self._doAxisCorrection.hide()

        self._useTomwerAxis = qt.QCheckBox(
            "use center of rotation computed upstream (if any)", parent=self
        )
        self._useTomwerAxis.setToolTip(
            "If selected, the value computed "
            "upstream in this flow will be used. \n"
            "This option has priority over "
            "other options"
        )
        self.layout().addWidget(self._useTomwerAxis)

        self._useOldTomwerAxis = qt.QCheckBox(
            "use center of rotation calculation from previous session (if any)",
            parent=self,
        )
        self._useOldTomwerAxis.setToolTip(
            "If the scan has already been processed by tomwer, "
            "the value of the center of rotation used had been recorded. \n"
        )
        self.layout().addWidget(self._useOldTomwerAxis)

        # add spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        # link the check box
        self.linkGroupWithH5Variable(
            group=self._doAxisCorrection,
            structID="FTAXIS",
            h5ParamName="DO_AXIS_CORRECTION",
            setter=self._setDoAxisCorrection,
            getter=self._getDoAxisCorrection,
        )
        self.linkGroupWithH5Variable(
            group=self._useTomwerAxis,
            structID="FTAXIS",
            h5ParamName="USE_TOMWER_AXIS",
            setter=self._setUseTomwerAxis,
            getter=self._getUseTomwerAxis,
        )
        self.linkGroupWithH5Variable(
            group=self._useOldTomwerAxis,
            structID="FTAXIS",
            h5ParamName="TRY_USE_OLD_TOMWER_AXIS",
            setter=self._setTryUseOldTomwerAxis,
            getter=self._getTryUseOldTomwerAxis,
        )

        self.linkCheckboxWithH5Variable(
            self._qcbHalfAcq, structID="FT", h5ParamName="HALF_ACQ"
        )

        # signal / Slot connection
        self._doAxisCorrection.toggled.connect(self._doAxisCorrectionChanged)
        self._useTomwerAxis.toggled.connect(self._useTomwerAxisChanged)
        self._useOldTomwerAxis.toggled.connect(self._useOldTomwerAxisChanged)
        self._qcbHalfAcq.toggled.connect(self._HALFACQChanged)

    def setReconsParams(self, recons_params):
        """
        Define the `.ReconsParams` that the widget edit. Those parameters will
        be copied in all the TomoBase process by the widget

        :param recons_params: tomographic parameter to edit
        :type recons_params: `.ReconsParams`
        """
        assert isinstance(recons_params, QReconsParams)

        if self._recons_params:
            self._recons_params.sigChanged.disconnect(self._update_params)
        self._recons_params = recons_params
        self.load(self._recons_params)
        self._recons_params.sigChanged.connect(self._update_params)

    def _update_params(self):
        """Update all parameter"""
        self.load(self._recons_params)

    def _setDoAxisCorrection(self, doAxisCorrrection: bool) -> None:
        assert type(doAxisCorrrection) is bool
        self._doAxisCorrection.setChecked(doAxisCorrrection)

    def _getDoAxisCorrection(self) -> bool:
        return self._doAxisCorrection.isChecked()

    def _setUseTomwerAxis(self, useTomwerAxis: bool) -> None:
        assert type(useTomwerAxis) is bool
        self._useTomwerAxis.setChecked(useTomwerAxis)

    def _getUseTomwerAxis(self) -> bool:
        return self._useTomwerAxis.isChecked()

    def _setTryUseOldTomwerAxis(self, useOldTomwerAxis: bool) -> None:
        assert type(useOldTomwerAxis) is bool
        self._useOldTomwerAxis.setChecked(useOldTomwerAxis)

    def _getTryUseOldTomwerAxis(self) -> bool:
        return self._useOldTomwerAxis

    def _doAxisCorrectionChanged(self, *args, **kwargs) -> None:
        doAxisCorrection = self._getDoAxisCorrection()
        self._recons_params["FTAXIS"]["DO_AXIS_CORRECTION"] = doAxisCorrection

    def _useTomwerAxisChanged(self, *args, **kwargs) -> None:
        self._recons_params["FTAXIS"]["USE_TOMWER_AXIS"] = self._getUseTomwerAxis()

    def _useOldTomwerAxisChanged(self, *args, **kwargs) -> None:
        self._recons_params["FTAXIS"][
            "TRY_USE_OLD_TOMWER_AXIS"
        ] = self._getTryUseOldTomwerAxis()

    def _HALFACQChanged(self, b):
        if int(b) != self._recons_params["FT"]["HALF_ACQ"]:
            self._recons_params["FT"]["HALF_ACQ"] = int(b)

    def setScan(self, scan):
        fov = scan.field_of_view
        if fov is not None:
            fov = _FOV.from_value(fov)
            self._qcbHalfAcq.setChecked(fov == _FOV.HALF)
