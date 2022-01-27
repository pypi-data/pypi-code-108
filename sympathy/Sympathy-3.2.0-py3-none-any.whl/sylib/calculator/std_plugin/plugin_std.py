# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import collections

from sylib.calculator import plugins
from sylib.calculator.std_plugin import (
    basics, logics, event_detection)


class StdPlugin(plugins.ICalcPlugin):
    """Standard plugin for calculator node."""

    # This plugin should be listed first:
    WEIGHT = -1

    @classmethod
    def plugin_impl_name(cls):
        return 'Standard'

    @staticmethod
    def gui_dict():
        gui_dict = collections.OrderedDict()
        gui_dict.update(basics.GUI_DICT)
        gui_dict.update(logics.GUI_DICT)
        gui_dict.update(event_detection.GUI_DICT)
        return gui_dict

    @staticmethod
    def globals_dict():
        return {'ca': plugins.PluginWrapper(basics.LogicOperator,
                                            basics.Statistics,
                                            logics.Logics,
                                            event_detection.EventDetection)}
