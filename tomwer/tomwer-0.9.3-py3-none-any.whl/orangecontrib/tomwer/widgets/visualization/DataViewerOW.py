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
from orangewidget import widget, gui
from orangewidget.widget import Input
from tomwer.gui.visualization.dataviewer import DataViewer
from tomwer.core.scan.scanbase import TomwerScanBase
from orangewidget import settings
from tomwer.gui import utils
from tomwer.gui import icons
import tomwer.core.process.visualization.dataviewer
import logging

_logger = logging.getLogger(__name__)


class DataViewerOW(widget.OWBaseWidget, openclass=True):
    """a data viewer able to:

    - display slices (latest reconstructed if any)
    - display radios with or without normalization

    :param parent: the parent widget
    """

    name = "data viewer"
    id = "orange.widgets.tomwer.dataviewer"
    description = "allow user too browse through data"
    icon = "icons/eye.png"
    priority = 70
    keywords = ["tomography", "file", "tomwer", "acquisition", "validation"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    ewokstaskclass = tomwer.core.process.visualization.dataviewer._DataViewerPlaceHolder

    _viewer_config = settings.Setting(dict())

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent)
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self.viewer = DataViewer(parent=self)
        self.viewer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        self._layout.addWidget(self.viewer)
        self._setSettings(settings=self._viewer_config)

        # open with ImageJ button
        types = qt.QDialogButtonBox.Apply
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)
        self._buttonOpenImageJ = self._buttons.button(qt.QDialogButtonBox.Apply)
        self._buttonOpenImageJ.setText("open with ImageJ")
        self._buttonOpenImageJ.setIcon(icons.getQIcon("Imagej_icon"))
        self.layout().addWidget(self._buttons)

        # connect signal / slot
        self.viewer.sigConfigChanged.connect(self._updateSettings)
        self._buttonOpenImageJ.released.connect(self._openCurrentInImagej)

    def _openCurrentInImagej(self):
        current_url = self.viewer.getCurrentUrl()

        if current_url is None:
            _logger.warning("No active image defined")
        else:
            try:
                utils.open_url_with_image_j(current_url)
            except OSError as e:
                msg = qt.QMessageBox(self)
                msg.setIcon(qt.QMessageBox.Warning)
                msg.setWindowTitle("Unable to open image in imagej")
                msg.setText(str(e))
                msg.exec_()

    @Inputs.data
    def addScan(self, scan):
        if scan is None:
            return
        self.viewer.setScan(scan)

    def sizeHint(self):
        return qt.QSize(400, 500)

    def _updateSettings(self):
        self._viewer_config["mode"] = self.viewer.getDisplayMode()
        self._viewer_config["slice_opt"] = self.viewer.getSliceOption()
        self._viewer_config["radio_opt"] = self.viewer.getRadioOption()

    def _setSettings(self, settings):
        old_state = self.viewer.blockSignals(True)
        if "mode" in settings:
            self.viewer.setDisplayMode(settings["mode"])
        if "slice_opt" in settings:
            self.viewer.setSliceOption(settings["slice_opt"])
        if "radio_opt" in settings:
            self.viewer.setRadioOption(settings["radio_opt"])
        self.viewer.blockSignals(old_state)

    def close(self):
        self.viewer.close()
        self.viewer = None
        super().close()
