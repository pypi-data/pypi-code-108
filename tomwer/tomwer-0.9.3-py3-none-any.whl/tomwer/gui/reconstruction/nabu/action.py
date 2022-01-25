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
__date__ = "04/08/2020"


from silx.gui import qt
from tomwer.gui import icons as tomwer_icons


class MinimalisticConfigurationAction(qt.QAction):
    """
    Action to display the 'minimalistic' options only
    """

    def __init__(self, parent):
        self.__icon = tomwer_icons.getQIcon("minimalistic_user")
        qt.QAction.__init__(self, self.__icon, "minimalistic options", parent)
        self.setIconVisibleInMenu(True)
        self.setCheckable(True)
        self.setToolTip(self.tooltip())

    def tooltip(self):
        return "configuration: minimalistic level limit the number of options"

    def icon(self):
        return self.__icon

    def text(self):
        return "Minimalistic configuration"


class BasicConfigurationAction(qt.QAction):
    """
    Action to display the 'basic' options only
    """

    def __init__(self, parent):
        self.__icon = tomwer_icons.getQIcon("basic_user")
        qt.QAction.__init__(self, self.__icon, "basic options", parent)
        self.setIconVisibleInMenu(True)
        self.setCheckable(True)
        self.setToolTip(self.tooltip())

    def tooltip(self):
        return "configuration: basic level limit the number of options"

    def icon(self):
        return self.__icon

    def text(self):
        return "Basic configuration"


class ExpertConfigurationAction(qt.QAction):
    """
    Action to display the 'advanced' / expert options
    """

    def __init__(self, parent):
        self.__icon = tomwer_icons.getQIcon("advanced_user")
        qt.QAction.__init__(self, self.__icon, "advanced options", parent)
        self.setIconVisibleInMenu(True)
        self.setCheckable(True)
        self.setToolTip(self.tooltip())

    def tooltip(self):
        return (
            "configuration: advanced level give user all the possible \n"
            "option to tune the reconstructions"
        )

    def icon(self):
        return self.__icon

    def text(self):
        return "Advanced configuration"


class FilterAction(qt.QAction):
    """
    Action to activate the filtering from the nabu stage
    """

    def __init__(self, parent):
        style = qt.QApplication.style()
        icon = style.standardIcon(qt.QStyle.SP_FileDialogContentsView)

        qt.QAction.__init__(self, icon, "filter configuration", parent)
        self.setToolTip(
            "If activated will only display the configuration"
            "for the active nabu phase"
        )
        self.setCheckable(True)
        self.setShortcut(qt.QKeySequence(qt.Qt.Key_F))
