# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
from sympathy.utils.components import get_components
from sympathy.api import component


class ICalcPlugin(component.NodePlugin):
    """Interface for calculator plugins."""

    WEIGHT = 10000

    @staticmethod
    def plugin_base_name():
        return 'Calculator'

    @staticmethod
    def gui_dict():
        """
        Return a dictionary with functions that will be shown in the
        configuration gui for the calculator node.

        Each dictionary in the globals_dict represents another level of
        subcategories in the tree view. The keys of the dict is used as labels
        for the subcategories. A list represents a list of functions.

        Each function in the list should be a tuple of three elements: label,
        code, tooltip/documentation.

        For example:

        {'My functions': [
            ('My function 1', 'myplugin.func1()',
             "My function 1 is awesome..."),
            ('My function 2', 'myplugin.func2()',
             "My function 1 is also awesome...")]}

        This should result in a top level category called "My functions"
        containing the two functions "My function 1" and "My function 2".
        """
        return {}

    @staticmethod
    def globals_dict():
        """
        Return a dictionary that will be added to the globals dictionary
        when executing calculations.
        """
        return {}

    @staticmethod
    def imports():
        """
        This method has no effect and will be removed in Sympathy 4.0.0.
        """
        return {}

    @staticmethod
    def hidden_items():
        """
        Reimplement this to hide some elements from other plugins.

        The hidden functions will still be available, but won't show up in the
        list of common functions in the calculator gui.

        The returned value should be a list of tuples with the "paths" in the
        gui_dict that should be hidden. E.g. ``[("Event detection",)]`` will
        hide the entire event detection subtree, while ``[("Event detection",
        "Changed")]`` will hide the function called "Changed" under "Event
        detection".
        """
        return []


class MatlabCalcPlugin(object):
    """Interface for calculator plugins."""

    WEIGHT = 10000

    @staticmethod
    def gui_dict(generic):
        """
        Return a dictionary with functions that will be shown in the
        configuration gui for the calculator node.
        """
        return {}

    @staticmethod
    def globals_dict():
        """
        Return a dictionary that will be added to the globals dictionary
        when executing calculations.
        """
        return {}


def available_plugins(backend='python'):
    """Return all available plugins derived for a specific backend."""
    plugin_classes = {'python': ICalcPlugin,
                      'matlab': MatlabCalcPlugin}
    return get_components('plugin_*.py', plugin_classes[backend])


def get_globals_dict(plugin):
    """
    Return a dictionary that will be added to the globals dictionary
    when executing calculations.
    """
    res = {}
    res.update(plugin.globals_dict())
    return res


class PluginWrapper(object):
    """
    Merge two or more module-like objects into one.

    getattr calls on PluginWrapper objects are passed on to the module-like
    objects and the first one which doesn't raise AttributeError gets to return
    its result.
    """

    def __init__(self, *namespaces):
        self._namespaces = list(namespaces)

    def __getattr__(self, attr):
        for ns in self._namespaces:
            try:
                return getattr(ns, attr)
            except AttributeError:
                pass

        raise AttributeError(attr)
