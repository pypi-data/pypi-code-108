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
__date__ = "21/07/2020"

from silx.gui import qt
from orangewidget import gui
from orangewidget.widget import Input, Output

import tomwer.core.process.control.scanvalidator
from tomwer.gui.control.datavalidator import DataValidator
from tomwer.core.scan.scanbase import TomwerScanBase
from orangecontrib.tomwer.orange.managedprocess import SuperviseOW
from processview.core.manager import ProcessManager, DatasetState
from tomwer.core.scan.scanbase import _TomwerBaseDock
from orangewidget import settings
from tomwer.utils import docstring
import logging

_logger = logging.getLogger(__name__)


class DataValidatorOW(SuperviseOW):
    """a data viewer able to:

    - display slices (latest reconstructed if any)
    - display radios with or without normalization

    :param parent: the parent widget
    """

    name = "data validator"
    id = "orange.widgets.tomwer.datavalidator"
    description = """Widget displaying results of a reconstruction and asking to
        the user if he want to validate or not the reconstruction. User can also ask
        for some modification on the reconstruction parameters"""
    icon = "icons/validator.png"
    priority = 23
    keywords = ["tomography", "file", "tomwer", "acquisition", "validation"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    ewokstaskclass = tomwer.core.process.control.scanvalidator._ScanValidatorPlaceHolder

    _viewer_config = settings.Setting(dict())

    _warnValManualShow = False
    """
    used to know if the message to inform user about `validate manually` has
    already been displayed.
    This informative message will be show under the following conditions:

        * the scanValidator contains at least `_NB_SCAN_BF_WARN`
        * this dialog have never been showed in the current session.
    """

    _NB_SCAN_BF_WARN = 10
    """
    Limit of stored scans before displaying the informative message about
    `validate manually` checkbox
    """

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    class Outputs:
        data = Output(name="data", type=TomwerScanBase)
        recons_params_changed = Output(
            name="change recons params",
            type=_TomwerBaseDock,
        )

    def __init__(self, parent=None):
        SuperviseOW.__init__(self, parent)
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self._widget = DataValidator(parent=self)
        self._layout.addWidget(self._widget)
        self._setSettings(settings=self._viewer_config)

        # connect signal / slots
        self._widget.sigChangeReconsParams.connect(self._changeReconsParamsEmited)
        self._widget.sigScanReady.connect(self._scanReadyEmitted)
        self._widget._centralWidget.sigConfigChanged.connect(self._updateSettings)

    def close(self):
        if self._widget is not None:
            self._widget.setAttribute(qt.Qt.WA_DeleteOnClose)
            self._widget.close()
            self._widget = None
        super().close()

    @Inputs.data
    def addScan(self, scan):
        if scan is None:
            return
        assert isinstance(scan, TomwerScanBase)
        self._widget.addScan(scan)
        ProcessManager().notify_dataset_state(
            dataset=scan, process=self, state=DatasetState.WAIT_USER_VALIDATION
        )
        # in the case the memory is full, the scan can have been already
        # validated and so not accessible
        if (
            self._warnValManualShow is False
            and len(self._widget._scansToValidate) >= self._NB_SCAN_BF_WARN
        ):
            mess = (
                "Please note that the scanValidator is actually storing %s "
                "scan(s). \n"
                "Scan need to be validated manually in order to continue "
                "the workflow processing. \n"
                "you can either validate scan manually or uncheck the "
                "`validate manually` check box." % self._NB_SCAN_BF_WARN
            )

            mess = qt.QMessageBox(self, qt.QMessageBox.Information, mess)
            mess.setModal(False)
            mess.show()
            self._warnValManualShow = True

        if self.isValidationManual():
            self.show()
            self.activateWindow()
            self.raise_()

    @docstring
    def reprocess(self, dataset):
        self.addScan(dataset)

    def isValidationManual(self):
        return self._widget.isValidationManual()

    def _changeReconsParamsEmited(self, scan):
        self.Outputs.recons_param_changed.send(scan)

    def _scanReadyEmitted(self, scan):
        ProcessManager().notify_dataset_state(
            dataset=scan, process=self, state=DatasetState.SUCCEED
        )
        self.Outputs.data.send(scan)

    def _updateSettings(self):
        viewer = self._widget._centralWidget
        self._viewer_config["mode"] = viewer.getDisplayMode()
        self._viewer_config["slice_opt"] = viewer.getSliceOption()
        self._viewer_config["radio_opt"] = viewer.getRadioOption()

    def _setSettings(self, settings):
        viewer = self._widget._centralWidget
        old_state = viewer.blockSignals(True)
        if "mode" in settings:
            viewer.setDisplayMode(settings["mode"])
        if "slice_opt" in settings:
            viewer.setSliceOption(settings["slice_opt"])
        if "radio_opt" in settings:
            viewer.setRadioOption(settings["radio_opt"])
        viewer.blockSignals(old_state)

    def getNScanToValidate(self):
        return len(self._widget._scansToValidate)

    def _validateScan(self, scan):
        self._widget._validateScan(scan=scan)

    def setAutomaticValidation(self, auto):
        self._widget.setAutomaticValidation(auto)
