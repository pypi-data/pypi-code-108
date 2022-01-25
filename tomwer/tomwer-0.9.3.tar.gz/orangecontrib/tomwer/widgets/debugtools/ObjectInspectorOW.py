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

__authors__ = [
    "H. Payno",
]
__license__ = "MIT"
__date__ = "30/09/2020"

from orangewidget import widget, gui
from tomwer.gui.debugtools.objectinspector import ObjectInspector
from orangewidget.widget import Input


class ObjectInspectorOW(widget.OWBaseWidget, openclass=True):
    """
    A simple widget to browse a TomwerScanBase object
    """

    name = "tomwer object browser"
    id = "orangecontrib.tomwer.widgets.debugtools.tomwerscanbasebrowser"
    description = "create on the fly dataset"
    icon = "icons/inspector.png"
    priority = 255
    keywords = ["tomography", "file", "tomwer", "dataset", "debug"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    class Inputs:
        data = Input(name="object", type=object)

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent=parent)
        self._layout = gui.vBox(self.mainArea, self.name).layout()
        self.inspector = ObjectInspector(parent=self)
        self._layout.addWidget(self.inspector)

    @Inputs.data
    def setObject(self, obj):
        self.inspector.setObject(obj)
