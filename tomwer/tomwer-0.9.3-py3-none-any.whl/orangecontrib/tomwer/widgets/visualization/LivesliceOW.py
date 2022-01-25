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

__authors__ = ["C. Nemoz", "H. Payno"]
__license__ = "MIT"
__date__ = "26/06/2018"

from orangewidget import widget, gui
from orangewidget.widget import Input
from tomwer.core.utils import getFirstProjFile
from tomwer.core.scan.scanbase import TomwerScanBase
import tomwer.core.process.visualization.liveslice

try:
    from liveslice.gui.liveslice_gui import ReconstructionApp
except ImportError:
    has_liveslice = False
else:
    has_liveslice = True
import logging

_logger = logging.getLogger(__name__)


if has_liveslice is True:

    class LiveSliceOW(widget.OWBaseWidget, openclass=True):
        """
        Simple widget displaying the live slice interface if found


        :param parent: the parent widget
        """

        name = "live slice"
        id = "orange.widgets.tomwer.liveslice"
        priority = 36
        icon = "icons/liveslice.png"
        keywords = ["tomography", "live slice", "reconstruction", "visualization"]

        ewokstaskclass = (
            tomwer.core.process.visualization.liveslice._LiveSlicePlaceHolder
        )

        want_main_area = True
        resizing_enabled = True
        compress_signal = False

        class Inputs:
            data = Input(name="data", type=TomwerScanBase)

        def __init__(self, parent=None):
            widget.OWBaseWidget.__init__(self, parent)
            layout = gui.vBox(self.mainArea, self.name).layout()
            self._mainWidget = ReconstructionApp()
            self._mainWidget.close_button.hide()
            layout.addWidget(self._mainWidget)

        @Inputs.data
        def updateScan(self, scanID):
            if scanID is not None:
                first_proj_file = getFirstProjFile(scanID)
                if first_proj_file is not None:
                    self._mainWidget.setSinoPath(first_proj_file)
                    self._mainWidget.initiate()
