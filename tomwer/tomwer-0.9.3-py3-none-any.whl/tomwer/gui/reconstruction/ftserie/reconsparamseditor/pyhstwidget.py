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
from tomwer.core.utils import pyhstutils
from tomwer.gui.reconstruction.ftserie.h5editor import H5StructEditor
from tomwer.synctools.ftseries import QReconsParams, _QPyhstRP
from tomwer.gui.reconstruction.deviceselector import CudaPlatfornGroup

logger = logging.getLogger(__name__)


class PyHSTWidget(H5StructEditor, qt.QWidget):
    """
    Definition of the PyHST tab to edit the PyHST parameters

    :param reconsparams: reconstruction parameters edited by the widget
    """

    def __init__(self, reconsparams, parent=None):
        qt.QWidget.__init__(self, parent)
        H5StructEditor.__init__(self, structID="PYHSTEXE")
        self._recons_params = None
        self.setReconsParams(recons_params=reconsparams)

        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.__buildPYHSTVersion())
        self.layout().addWidget(self.__buildPYHSTOfficialVersion())

        self._qcbverbose = qt.QCheckBox("verbose", parent=self)
        self.layout().addWidget(self._qcbverbose)
        self.linkCheckboxWithH5Variable(self._qcbverbose, "VERBOSE", invert=False)

        self.layout().addWidget(self.__buildVerboseFile())
        self.layout().addWidget(self.__buildMakeOAR())
        self.layout().addWidget(self.__buildCudaOptions())

        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer)

        self._qcbverbose.setChecked(False)
        self._versoseFileWidget.setVisible(True)
        self._qcbverbose.toggled.connect(self._versoseFileWidget.setDisabled)

        self._makeConnection()
        # expose API
        self.getCudaDevices = self._cudaSelector.getExistingDevices

    def setReconsParams(self, recons_params):
        if isinstance(recons_params, QReconsParams):
            _recons_params = recons_params.pyhst
        elif isinstance(recons_params, _QPyhstRP):
            _recons_params = recons_params
        else:
            raise ValueError(
                "recons_params should be an instance of QReconsParam or _QPyhstRP"
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
        self._qcbverbose.toggled.connect(self._verboseChanged)
        self._qcbPyHSTVersion.currentIndexChanged.connect(self._pyHSTVersionChanged)
        self._qleVerboseFile.editingFinished.connect(self._verboseFileChanged)
        self._makeOARFileCB.toggled.connect(self._makeOARChanged)
        self._cudaSelector.selectionChanged.connect(self._cudaDevicesChanged)

    def _verboseChanged(self, b):
        self._recons_params["VERBOSE"] = b

    def __buildPYHSTVersion(self):
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())

        # create the PyHST version combobox
        widget.layout().addWidget(qt.QLabel("PyHST version : ", parent=widget))
        self._qcbPyHSTVersion = qt.QComboBox(parent=self)
        widget.layout().addWidget(self._qcbPyHSTVersion)
        self.linkComboboxWithH5Variable(
            self._qcbPyHSTVersion, "EXE", fitwithindex=False, setDefault=False
        )

        # try to get the PyHST dir
        d = pyhstutils._getPyHSTDir()
        if d is None:
            raise logger.warning(
                """Can't find the directory containing the PyHST
                directory. Please set the environment variable
                PYHST_DIR and run again"""
            )

        availablePyHSTVersion = pyhstutils._findPyHSTVersions(d)
        availablePyHSTVersion.extend(pyhstutils._getPyHSTFromEnvVariable())
        if len(availablePyHSTVersion) == 0:
            self.__warmNoPyHSTFound(d)
            pass
        else:
            [self._qcbPyHSTVersion.addItem(exe) for exe in availablePyHSTVersion]

        return widget

    def __buildMakeOAR(self):
        self._makeOARFileCB = qt.QCheckBox("make OAR file", parent=self)
        self.linkCheckboxWithH5Variable(
            qcheckbox=self._makeOARFileCB, h5ParamName="MAKE_OAR_FILE"
        )
        self._makeOARFileCB.toggled.connect(self._makeOARChanged)
        return self._makeOARFileCB

    def __buildCudaOptions(self):
        self._cudaSelector = CudaPlatfornGroup(parent=self)
        # by default activate all cuda device
        self._cudaSelector.activate_all()
        self.linkGroupWithH5Variable(
            group=self._cudaSelector,
            h5ParamName="CUDA_DEVICES",
            setter=self._cudaSelector.setDevices,
            getter=self._cudaSelector.getSelectedDevices,
        )
        old = self._recons_params.blockSignals(True)
        self._recons_params["CUDA_DEVICES"] = self._cudaSelector.getSelectedDevices()
        self._recons_params.blockSignals(old)

        return self._cudaSelector

    def _pyHSTVersionChanged(self):
        value = self._qcbPyHSTVersion.currentText()
        self._recons_params["EXE"] = value

    def _makeOARChanged(self, b):
        self._recons_params["MAKE_OAR_FILE"] = b

    def _cudaDevicesChanged(self, devices):
        self._recons_params.cuda_devices = devices

    def __buildPYHSTOfficialVersion(self):
        """build the official version QLine edit and update the _qcbPyHSTVersion
        combobox so should always be called after.
        """
        widget = qt.QWidget(self)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(qt.QLabel("PyHST official version", parent=widget))
        self._qlOfficalVersion = qt.QLabel("", parent=widget)
        widget.layout().addWidget(self._qlOfficalVersion)
        self.linkGroupWithH5Variable(
            self._qlOfficalVersion,
            "OFFV",
            getter=self._qlOfficalVersion.text,
            setter=self._qlOfficalVersion.setText,
        )
        return widget

    def __warmNoPyHSTFound(self, directory):
        """Simple function displaying a MessageBox that PyHST haven't been found"""
        text = "No executable of PyHST have been found in %s." % directory
        text += " You might set the environment variable PYHST_DIR "
        text += " or install PyHST."
        logger.info(text)

    def __buildVerboseFile(self):
        self._versoseFileWidget = qt.QWidget(self)
        self._versoseFileWidget.setLayout(qt.QHBoxLayout())
        self._versoseFileWidget.layout().addWidget(
            qt.QLabel("name of the PyHST information output file", parent=self)
        )
        self._qleVerboseFile = qt.QLineEdit("", parent=None)
        self._versoseFileWidget.layout().addWidget(self._qleVerboseFile)
        self.LinkLineEditWithH5Variable(self._qleVerboseFile, "VERBOSE_FILE")
        return self._versoseFileWidget

    def _verboseFileChanged(self):
        value = self._qleVerboseFile.text()
        self._recons_params._set_parameter_value(parameter="VERBOSE_FILE", value=value)
