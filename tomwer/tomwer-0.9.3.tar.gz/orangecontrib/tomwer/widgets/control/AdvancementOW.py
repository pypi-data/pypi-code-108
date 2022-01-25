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
__date__ = "10/01/2018"


import logging
from orangewidget import widget, gui
from processview.gui.processmanager import ProcessManagerWindow

logger = logging.getLogger(__name__)


class AdvancementOW(widget.OWBaseWidget, openclass=True):
    """
    A simple widget managing the copy of an incoming folder to an other one

    :param parent: the parent widget
    """

    # note of this widget should be the one registred on the documentation
    name = "advancement"
    id = "orangecontrib.widgets.tomwer.control.AdvancementOW.AdvancementOW"
    description = "This widget can display advancement of processes and scans"
    icon = "icons/advancement.svg"
    priority = 5
    keywords = ["tomography", "process", "advancement"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent)

        self._widget = ProcessManagerWindow(parent=self)

        self._box = gui.vBox(self.mainArea, self.name)
        layout = self._box.layout()
        layout.addWidget(self._widget)
