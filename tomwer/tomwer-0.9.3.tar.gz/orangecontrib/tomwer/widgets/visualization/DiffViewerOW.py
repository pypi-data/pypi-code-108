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
__date__ = "07/09/2020"

from silx.gui import qt
from orangewidget import widget, gui
from orangewidget.widget import Input
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.visualization.diffviewer import DiffFrameViewer
import tomwer.core.process.visualization.diffviewer
import logging

_logger = logging.getLogger(__name__)


class DiffViewerOW(widget.OWBaseWidget, openclass=True):
    """
    Associate TomoScanBase with the silx's ComparaImage tool.
    Allows to compare two random frame.
    """

    name = "diff viewer"
    id = "orangecontrib.tomwer.widgets.visualization.diffviewerow"
    description = "Allows comparison between two random frame from a scan"
    icon = "icons/diff.png"
    priority = 107
    keywords = ["tomography", "diff", "tomwer", "compare", "comparison"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    ewokstaskclass = tomwer.core.process.visualization.diffviewer._DiffViewerPlaceHolder

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent)
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self.viewer = DiffFrameViewer(parent=self)
        self._layout.addWidget(self.viewer)

    @Inputs.data
    def addScan(self, scan):
        if scan is None:
            return
        self.viewer.addScan(scan)

    def sizeHint(self):
        return qt.QSize(400, 500)
