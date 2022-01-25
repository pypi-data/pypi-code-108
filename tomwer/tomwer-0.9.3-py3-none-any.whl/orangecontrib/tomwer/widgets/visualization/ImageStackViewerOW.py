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
__date__ = "01/12/2016"

from silx.gui import qt
from orangewidget import widget, gui
from orangewidget.widget import Input
from tomwer.core.scan.scanfactory import ScanFactory
from tomwer.gui.viewerqwidget import ScanWidget
from tomwer.core.scan.scanbase import TomwerScanBase
import tomwer.core.process.visualization.imagestackviewer
import logging

logger = logging.getLogger(__name__)


class ImageStackViewerOW(widget.OWBaseWidget, openclass=True):
    """a simple viewer of image stack

    :param parent:the parent widget
    :param FtserieReconstruction ftseries: the initial reconstruction to show
    """

    name = "(old) data viewer"
    id = "orange.widgets.tomwer.imagestackviewer"
    description = "Show a small recap of the reconstruction runned"
    icon = "icons/eyecrack.png"
    priority = 700
    keywords = ["tomography", "file", "tomwer", "acquisition", "validation"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    ewokstask = (
        tomwer.core.process.visualization.imagestackviewer._ImageStackViewerPlaceHolder
    )

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None, ftseries=None):
        widget.OWBaseWidget.__init__(self, parent)

        self.tabsWidget = {}
        # building GUI
        self._scanWidgetLayout = gui.vBox(self.mainArea, self.name).layout()
        self.viewer = ScanWidget(parent=self, canLoadOtherScan=False)

        self._scanWidgetLayout.addWidget(self.viewer)
        self._scanWidgetLayout.setContentsMargins(0, 0, 0, 0)
        if ftseries is not None:
            self.viewer.updateData(ftseries)

    @Inputs.data
    def addScan(self, ftseriereconstruction):
        if ftseriereconstruction is None:
            return

        _ftserie = ftseriereconstruction
        if type(ftseriereconstruction) is str:
            _ftserie = ScanFactory.create_scan_object(_ftserie)
        assert isinstance(_ftserie, TomwerScanBase)
        return self.viewer.updateData(_ftserie)

    def updateFromPath(self, path):
        if path is not None:
            return self.viewer.updateFromPath(path)

    def sizeHint(self):
        return qt.QSize(400, 500)
