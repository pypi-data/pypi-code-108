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

import pytest
from silx.gui import qt
from orangewidget import widget, gui
from orangewidget.widget import Input
from tomwer.gui.visualization.volumeviewer import VolumeViewer
from tomwer.core.scan.scanbase import TomwerScanBase
import tomwer.core.process.visualization.volumeviewer


@pytest.mark.skip("Fail on CI")
class VolumeViewerOW(widget.OWBaseWidget, openclass=True):
    """a viewer to display the last volume reconstructed using silx plot3d
    viewer.

    :param parent: the parent widget
    """

    name = "volume viewer"
    id = "orange.widgets.tomwer.visualization.VolumeViewerOW.VolumeViewerOW"
    description = "display the last volume reconstructed"
    icon = "icons/volumeviewer.svg"
    priority = 80
    keywords = ["tomography", "file", "tomwer", "acquisition", "validation"]

    ewokstaskclass = (
        tomwer.core.process.visualization.volumeviewer._VolumeViewerPlaceHolder
    )

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent)
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self.viewer = VolumeViewer(parent=self)
        self._layout.addWidget(self.viewer)

    @Inputs.data
    def addScan(self, scan):
        if scan is None:
            return
        self.viewer.setScan(scan)

    def sizeHint(self):
        return qt.QSize(400, 500)
