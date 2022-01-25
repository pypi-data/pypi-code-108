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
__date__ = "18/02/2018"


from tomwer.gui import icons as tomwericons
from silx.gui import qt


class HistoryAction(qt.QAction):
    """
    Action displaying the history of finished scans
    """

    def __init__(self, parent):
        icon = tomwericons.getQIcon("history")
        qt.QAction.__init__(self, icon, "history", parent)
        self.setCheckable(True)


class ConfigurationAction(qt.QAction):
    """
    Action to show the configuration dialog
    """

    def __init__(self, parent):
        icon = tomwericons.getQIcon("parameters")
        qt.QAction.__init__(self, icon, "configuration", parent)
        self.setCheckable(True)


class ObservationAction(qt.QAction):
    """
    Action to show the observation dialog
    """

    def __init__(self, parent):
        icon = tomwericons.getQIcon("loop")
        qt.QAction.__init__(self, icon, "observations", parent)
        self.setCheckable(True)


class ControlAction(qt.QAction):
    """
    Action to control the datawatcher (see status and select folder)
    """

    def __init__(self, parent):
        icon = tomwericons.getQIcon("health")
        qt.QAction.__init__(self, icon, "control", parent)
        self.setCheckable(True)
