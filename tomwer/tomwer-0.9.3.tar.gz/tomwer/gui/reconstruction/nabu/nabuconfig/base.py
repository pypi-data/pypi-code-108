# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
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
__date__ = "11/02/2020"


from typing import Union
from tomwer.core.process.reconstruction.nabu.utils import _NabuStages
from tomwer.core.process.reconstruction.nabu.utils import ConfigurationLevel


class _FilteringObject:
    """
    Simple class to define if the widget should be visible or not if visible
    (at some moment the 'option' wudget should be visible) and if filtered.
    Should avoid some conflict when set set visible
    """

    def __init__(self, widget):
        self._widget = widget
        self._visible = True
        # is this
        self._filtered = False

    def setVisible(self, visible):
        self._visible = visible
        self._updateVisibility()

    def setFiltered(self, filtered):
        self._filtered = filtered
        self._updateVisibility()

    def _updateVisibility(self):
        self._widget.setVisible(self._visible and self._filtered)


class _NabuStageConfigBase:
    """Define interface for a specific nabu stage configuration widget
    (or a part of the stage configuration)
    """

    def __init__(self, stage: Union[_NabuStages, str]):
        self.__stage = _NabuStages.from_value(stage)
        self._registeredWidgets = {}
        # list required widgets. Key is widget, value is the configuration
        # level

    def registerWidget(self, widget, config_level):
        """register a widget with a configuration level.

        :returns: _FilteringObject to use to define widget visibility
        """
        filteringObj = _FilteringObject(widget=widget)
        self._registeredWidgets[filteringObj] = ConfigurationLevel.from_value(
            config_level
        )
        return filteringObj

    def getConfiguration(self) -> dict:
        raise NotImplementedError("Base class")

    def setConfiguration(self, config) -> None:
        raise NotImplementedError("Base class")

    def getStage(self) -> _NabuStages:
        return self.__stage

    def setConfigurationLevel(self, level):
        for widget in self._registeredWidgets:
            filtered = self._registeredWidgets[widget] <= level
            widget.setFiltered(filtered)
