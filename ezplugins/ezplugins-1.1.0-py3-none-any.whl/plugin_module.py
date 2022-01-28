#
# SPDX-License-Identifier: MIT
#
# Copyright (C) 2019-2021, AllWorldIT.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""EZPlugins module class."""

import importlib
import inspect
import logging
import sys
from types import ModuleType
from typing import List

from .plugin import EZPlugin


class EZPluginModule:
    """
    Representation of a module within the plugin package hierarchy, which may contain plugins.

    If there is no plugins and no load exception, the module will not be added to the modules list.

    See :attr:`ezplugins.manager.EZPluginManager.modules` for how to get a list of loaded modules.

    Parameters
    ----------
    module_name : :class:`str`
        Name of the module.

    """

    _module: ModuleType
    _module_name: str
    _plugins: List[EZPlugin]

    def __init__(self, module_name: str):
        """
        Representation of a module within the plugin package hierarchy, which may contain plugins.

        If there is no plugins and no load exception, the module will not be added to the modules list.

        The module is first attempted to be loaded from system modules and already imported modules with failback trying to import
        it.

        See :attr:`ezplugins.manager.EZPluginManager.modules` for how to get a list of loaded modules.

        Parameters
        ----------
        module_name : :class:`str`
            Name of the module.

        """

        # Start off with the module being None and an empty plugin list
        self._module_name = module_name
        self._plugins = []

        logging.debug("EZPLUGINS => MODULE NAME: %s", module_name)

        # Check if module is loaded
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            # Try import
            module = importlib.import_module(module_name)

        self._module = module

        # Loop with class names
        for (_, plugin_class) in inspect.getmembers(self._module, inspect.isclass):

            # Only add classes that were marked as EZPlugins
            if not getattr(plugin_class, "_is_ezplugin", False):
                continue
            # Save plugin
            self._plugins.append(EZPlugin(plugin_class()))
            logging.debug(
                "EZPlugin loaded from '%s', class '%s'",
                self.module_name,
                plugin_class.__name__,
            )

    @property
    def module(self) -> ModuleType:
        """
        Property containing the imported module.

        Returns
        -------
        Optional[:class:`ModuleType`] :
            Module that was imported (if it was imported, or None).

        """
        return self._module

    @property
    def module_name(self) -> str:
        """
        Property containing the name of the module.

        Returns
        -------
        :class:`str` :
            Module name.

        """
        return self._module_name

    @property
    def plugins(self) -> List[EZPlugin]:
        """
        Property containing a list of EZPlugin's that belong to this module.

        Returns
        -------
        List[:class:`ezplugins.plugin.EZPlugin`] :
            List of instantiated EZPlugin's that represent the plugin objects that were instantiated.

        """
        return self._plugins
