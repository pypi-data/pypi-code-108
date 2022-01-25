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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "10/01/2018"


import functools
import logging
import os
import copy
from silx.gui import qt
from ..utils import WidgetLongProcessing
from orangewidget import settings
from orangewidget import gui
from orangewidget.widget import Input, Output
from orangecontrib.tomwer.orange.settings import CallbackSettingsHandler
from tomwer.core.process.reconstruction.lamino import LaminoReconstruction
from tomwer.gui.reconstruction.lamino.tofu import TofuWindow
from tomwer.synctools.stacks.reconstruction.lamino import LaminoReconstructionStack
import tomwer.core.process.reconstruction.lamino.tofu
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.utils import docstring
from ...orange.managedprocess import SuperviseOW

_logger = logging.getLogger(__name__)


class TofuOW(WidgetLongProcessing, SuperviseOW):
    """
    A simple widget managing the copy of an incoming folder to an other one

    :param parent: the parent widget
    """

    # note of this widget should be the one registered on the documentation
    name = "tofu reconstruction"
    id = "orange.widgets.tomwer.reconstruction.TofuOW.TofuOW"
    description = "This widget will call tofu for running a reconstruction "
    icon = "icons/XY_lamino.svg"
    priority = 25
    keywords = ["tomography", "tofu", "reconstruction", "lamino", "laminography"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    settingsHandler = CallbackSettingsHandler()

    ewokstaskclass = tomwer.core.process.reconstruction.lamino.tofu.LaminoReconstruction

    _reconsParams = settings.Setting(dict())
    """Parameters directly editabled from the TOFU interface"""
    # kept for compatibility
    static_input = settings.Setting({"data": None, "lamino_params": None})

    _additionalOpts = settings.Setting(dict())
    """Parameters which can be add on the expert tab from TOFU"""
    _delete_existing = settings.Setting(bool())
    """Should we remove the output directory if exists already"""

    class Inputs:
        data = Input(name="data", type=TomwerScanBase, doc="one scan to be process")

    class Outputs:
        data = Output(name="data", type=TomwerScanBase, doc="one scan to be process")

    def __init__(self, parent=None):
        SuperviseOW.__init__(self, parent=parent)
        WidgetLongProcessing.__init__(self)
        self._lastScan = None
        self._box = gui.vBox(self.mainArea, self.name)
        self._mainWidget = TofuWindow(parent=self)
        self._box.layout().addWidget(self._mainWidget)
        self._widgetControl = qt.QWidget(self)
        self._widgetControl.setLayout(qt.QHBoxLayout())
        self._executeButton = qt.QPushButton("reprocess", self._widgetControl)
        self._executeButton.clicked.connect(self._reprocess)
        self._executeButton.setEnabled(False)
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self._widgetControl.layout().addWidget(spacer)
        self._widgetControl.layout().addWidget(self._executeButton)

        self._box.layout().addWidget(self._mainWidget)
        self._box.layout().addWidget(self._widgetControl)

        lamino_params = self.static_input.get("lamino_params", None)
        if lamino_params is None:
            lamino_params = self._reconsParams
        self._mainWidget.setParameters(lamino_params)
        if len(self._additionalOpts) > 0:
            self._mainWidget.setAdditionalRecoOptions(self._additionalOpts)
        self._mainWidget.setRemoveOutputDir(self._delete_existing)

        self.settingsHandler.addCallback(self._updateSettingsVals)

        self._reconsStack = LaminoReconstructionStack(process_id=self.process_id)

        # signal / slot connections
        self._reconsStack.sigReconsStarted.connect(self.__processing_start)
        self._reconsStack.sigReconsFinished.connect(self.__processing_end)
        self._reconsStack.sigReconsFailed.connect(self.__processing_end)
        self._reconsStack.sigReconsMissParams.connect(self.__processing_end)

    @Inputs.data
    def process(self, scan):
        if scan is not None:
            assert isinstance(scan, TomwerScanBase)
            scan_ = copy.copy(scan)
            self._executeButton.setEnabled(True)
            self._lastScan = scan_
            self._mainWidget.loadFromScan(scan_.path)
            recons_param = self._mainWidget.getParameters()
            add_options = self._mainWidget.getAdditionalRecoOptions()
            # TODO: should be recorded in self._viewer widget

            remove_existing = self._mainWidget.removeOutputDir()

            callback = functools.partial(self.Outputs.data.send, scan_)
            self._reconsStack.add(
                recons_obj=LaminoReconstruction(),
                scan_id=scan_,
                recons_params=recons_param,
                additional_opts=add_options,
                remove_existing=remove_existing,
                callback=callback,
            )

    @docstring(SuperviseOW)
    def reprocess(self, dataset):
        self.process(dataset)

    def _reprocess(self):
        if self._lastScan is None:
            _logger.warning("No scan has been process yet")
        elif os.path.isdir(self._lastScan) is False:
            _logger.warning("Last scan %s, does not exist anymore" % self._lastScan)
            self._executeButton.setEnabled(False)
        else:
            self.process(self._lastScan)

    def _updateSettingsVals(self):
        """function used to update the settings values"""
        self._reconsParams = self._mainWidget.getParameters()
        self.lamino_params = {
            "data": None,
            "lamino_params": self._mainWidget.getParameters(),
        }

        self._additionalOpts = self._mainWidget.getAdditionalRecoOptions()
        self._delete_existing = self._mainWidget.removeOutputDir()

    def __processing_start(self, scan):
        self.processing_state(scan=scan, working=True)

    def __processing_end(self, scan):
        self.processing_state(scan=scan, working=False)

    def processing_state(self, scan, working: bool) -> None:
        # default orange version don't have Processing.
        try:
            if working:
                self.processing_info("processing %s" % scan.path)

            else:
                self.Processing.clear()
        except Exception:
            pass
