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
__date__ = "04/05/2018"


from orangewidget import widget, gui
from orangewidget.widget import Input
from tomwer.gui.stacks import SliceStack
from tomwer.core.scan.scanbase import TomwerScanBase
import tomwer.core.process.visualization.slicestack
import logging

logger = logging.getLogger(__name__)


class SlicesStackOW(widget.OWBaseWidget, openclass=True):
    """
    This widget will make copy or virtual link to all received *slice* files
    in order to group them all in one place and be able to browse those
    (using the image stack of view in orange or a third software as silx view)

    Options are:
       - copy files or create sym link (set to sym link)
       - overwrite if existing (set to False)

    Behavior:
        When the process receives a new data path ([scanPath]/[scan]) and if
        no output folder has been defined manually them it will try to create
        the folder [scanPath]/slices if not existing in order to redirect
        the slices files.
        If fails will ask for a directory.
        If the output folder is already existing then move directly to the
        copy.
    """

    name = "slice stack"
    id = "orange.widgets.tomwer.slicesstack.slicesstack"
    description = (
        "This widget will save all scan path given to here "
        "and extract received *slice* files with there shortest"
        "unique basename to be able to browse them"
    )

    icon = "icons/slicesstack.svg"
    priority = 26
    keywords = ["tomography", "slices", "tomwer", "stack", "group"]

    ewokstaskclass = tomwer.core.process.visualization.slicestack._SliceStackPlaceHolder

    allows_cycle = True
    compress_signal = False

    want_main_area = True
    resizing_enabled = True

    class Inputs:
        data = Input(name="data", type=TomwerScanBase)

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent)
        self._box = gui.vBox(self.mainArea, self.name)
        self._viewer = SliceStack(parent=self)
        self._box.layout().addWidget(self._viewer)

    @Inputs.data
    def addLeafScan(self, scanID):
        if scanID is None:
            return
        self._viewer.addLeafScan(scanID)
