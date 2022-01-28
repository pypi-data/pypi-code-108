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

"""EZPlugins manager."""

import logging
import pkgutil
import re
import sys
from typing import Dict, Iterator, List, Optional, Tuple

from .exceptions import EZPluginMethodNotFoundException
from .plugin import EZPlugin
from .plugin_method import EZPluginMethod
from .plugin_module import EZPluginModule


class EZPluginManager:
    """
    The :class:`~EZPluginManager` is responsible for both loading and returning plugin methods for execution.

    Loading plugins from packages can be done as follows, these packages are recursed and all classes decorated as being EZPlugin's
    are instantiated.::

        import ezplugins

        # Load plugins from mypackage.plugins and "mypackage2.plugins"
        plugin_manager = ezplugins.EZPluginManager()
        plugin_manager.load_package("mypackage.plugins")
        plugin_manager.load_package("mypackage2.plugins")

    Loading plugins from modules can be done, these modules are searched in the system module list first (which includes
    already-loaded modules), and falls back to attempting an import::

        import ezplugins

        # Load plugins from mypackage.plugin
        plugin_manager = ezplugins.EZPluginManager()
        plugin_manager.load_module("mypackage.plugin")

    All plugin modules matching a regex can also be loaded, these modules are searched in the system module list first (which
    includes already-loaded modules)::

        import ezplugins

        # Load plugins from mypackage.plugin
        plugin_manager = ezplugins.EZPluginManager()
        plugin_manager.load_module("mypackage.plugin")

    Plugins are mapped using their fully qualified name ``full.module.name#ClassName`` and their class name ``#ClassName``. Aliases
    can be created used for grouping or easier reference using :func:`~ezplugins.decorators.ezplugin_metadata`.

    For calling plugin methods see :meth:`~EZPluginManager.methods`.

    """

    _modules: List[EZPluginModule]

    def __init__(self) -> None:
        """
        Initialize EZPluginsCollection.

        Plugins are mapped with the below names:
            full.module.name#ClassName
            #ClassName

        Calling a plugin by name where multiple names match will result in all plugins being called.

        """

        # Initialize the module list we loaded plugins from
        self._modules = []

    def methods(
        self,
        where_name: Optional[str] = None,
        from_plugin: Optional[str] = None,
    ) -> Iterator[Tuple[EZPluginMethod, EZPlugin]]:
        """
        Return a generator used to iterate over plugin methods with a specific name and optionally from a specific plugin.

        An example of running all ``some_func`` methods in all plugins can be found below::

            # Call the method some_func in each plugin
            for method, _ in plugin_manager.methods(with_name="some_func"):
                result = method.run("param1", "param2")
                print(f"RESULT: {result}")

        As you can see in the above examples we have a ``_`` in the `for`, this is the :class:`~ezplugins.plugin.EZPlugin` plugin
        object which we didn't need::

            # Call the method some_func in each plugin
            for method, plugin in plugin_manager.methods(with_name="some_func"):
                result = method.run("param1", "param2")
                print(f"RESULT: {result} fomr {method.name}, plugin {plugin.fqn}")

        One can also call every single method marked as an :class:`~ezplugins.plugin.EZPlugin` method in all plugins using the
        following::

            # Call the method some_func in each plugin
            for method, _ in plugin_manager.methods():
                result = method.run("param1", "param2")
                print(f"RESULT: {result}")

        Calling a plugin by name where multiple names match based on class or alias will result in all plugins being called.

        Parameters
        ----------
        where_name : Optional[:class:`str`]
            Limit methods returned to those matching the name provided.

        from_plugin : Optional[:class:`str`]
            Limit methods returned to those belonging to a specific plugin.

        Returns
        -------
        Iterator[Tuple[:class:`~ezplugins.plugin_method.EZPluginMethod`, :class:`~ezplugins.plugin.EZPlugin`]] :
            A generator that provides tuples in the format of (:class:`~ezplugins.plugin_method.EZPluginMethod`,
            :class:`~ezplugins.plugin.EZPlugin`).

        """

        # Work out the plugins and methods we're going to call
        # Methods are unique, we'll be calling in order of method.order
        found_methods: Dict[EZPluginMethod, EZPlugin] = {}

        # Loop with our plugins matching the provided plugin_name or None
        for plugin in [x for x in self.plugins if from_plugin in [None, x.fqn, x.name, x.alias]]:
            # Loop with methods matching the method name
            for method in [x for x in plugin.methods if where_name in [None, x.name]]:
                # Check if plugin is in our call queue
                found_methods[method] = plugin

        # If we didn't find any methods, raise an exception
        if not found_methods:
            raise EZPluginMethodNotFoundException(method_name=where_name, plugin_name=from_plugin)

        # Loop with the ordered methods
        for method, plugin in sorted(found_methods.items(), key=lambda x: x[0].order):
            yield (method, plugin)

    def get_plugin(self, plugin_name: str) -> set[EZPlugin]:
        """
        Return a plugin with a given name.

        This will match on the fully qualified plugin name, the class name and aliase.

        Parameters
        ----------
        plugin_name : :class:`str`
            Plugin to call the method in.

        Returns
        -------
        set[ :class:`~ezplugins.plugin.EZPlugin` ] :
            Set of :class:`~ezplugins.plugin.EZPlugin` objects which matches the criteria.

        """

        plugin_set = set()

        # Loop with our plugins
        for plugin in self.plugins:
            # Add plugins which match the specified name
            if plugin_name in (plugin.fqn, plugin.name, plugin.alias):
                plugin_set.add(plugin)

        return plugin_set

    def load_package(self, package_name: str) -> None:  # noqa: C901, pylint: disable=too-many-branches
        """
        Recursively search the package package_name and retrieve all plugins.

        Classes ending in "Base" are excluded.

        Loading plugins from packages, these packages are recursed and all classes decorated as being EZPlugin's
        are instantiated.::

            import ezplugins

            # Load plugins from mypackage.plugins and "mypackage2.plugins"
            plugin_manager = ezplugins.EZPluginManager()
            plugin_manager.load_package("mypackage.plugins")
            plugin_manager.load_package("mypackage2.plugins")

        Parameters
        ----------
        package_name : :class:`str`
            Package to load plugins from.

        """

        logging.debug("Finding plugins in package '%s'", package_name)

        package = EZPluginModule(package_name)

        # Add base package module, but only if it has plugins
        if package.plugins:
            self._modules.append(package)

        # Grab some things we'll need below
        base_package_path = package.module.__path__
        base_package_name = package.module.__name__

        # Iterate through the modules
        for _, module_name, ispkg in pkgutil.iter_modules(base_package_path, base_package_name + "."):
            # If this is a sub-package, we need to process it later
            if ispkg:
                self.load_package(module_name)
                continue
            # Grab plugin module
            plugin_module = EZPluginModule(module_name)
            # If we loaded OK and don't have plugins, don't add to the plugin modules list
            if not plugin_module.plugins:
                logging.debug("Ignoring plugin module '%s': No plugins", plugin_module.module_name)
                continue
            # Add to the plugin modules list
            logging.debug("Adding plugin module: %s (%s plugins)", plugin_module.module_name, len(plugin_module.plugins))
            self._modules.append(plugin_module)

    def load_module(self, module_name: str) -> None:  # noqa: C901, pylint: disable=too-many-branches
        """
        Load plugins from a module.

        Classes ending in "Base" are excluded.

        Load plugins from modules, these modules are searched in the system module list first (which includes already-loaded
        modules), and falls back to attempting an import::

            import ezplugins

            # Load plugins from mypackage.plugin
            plugin_manager = ezplugins.EZPluginManager()
            plugin_manager.load_module("mypackage.plugin")

        Parameters
        ----------
        module_name : :class:`str`
            Module to load plugins from.

        """

        logging.debug("Finding plugins in module '%s'", module_name)

        # Grab plugin module
        plugin_module = EZPluginModule(module_name)
        # If we loaded OK and don't have plugins, don't add to the plugin modules list
        if not plugin_module.plugins:
            logging.debug("Ignoring plugin module '%s': No plugins", plugin_module.module_name)
            return
        # Add to the plugin modules list
        logging.debug("Adding plugin module: %s (%s plugins)", plugin_module.module_name, len(plugin_module.plugins))
        self._modules.append(plugin_module)

    def load_modules(self, matching: str) -> None:  # noqa: C901, pylint: disable=too-many-branches
        """
        Load plugins from modules matching a regex.

        Classes ending in "Base" are excluded.

        All plugin modules matching a regex can also be loaded, these modules are searched in the system module list first
        (which includes already-loaded modules)::

            import ezplugins

            # Load plugins from mypackage.plugin
            plugin_manager = ezplugins.EZPluginManager()
            plugin_manager.load_modules(r"^mypackage.plugin.")

        Parameters
        ----------
        matching : :class:`str`
            Regular expression to match modules to load.

        """

        logging.debug("Finding plugins in modules matching '%s'", matching)

        for module_name in sys.modules.copy():
            # Skip modules that don't match
            if not re.match(matching, module_name):
                continue
            # Grab plugin module
            plugin_module = EZPluginModule(module_name)
            # If we loaded OK and don't have plugins, don't add to the plugin modules list
            if not plugin_module.plugins:
                logging.debug("Ignoring plugin module '%s': No plugins", plugin_module.module_name)
                continue
            # Add to the plugin modules list
            logging.debug("Adding plugin module: %s (%s plugins)", plugin_module.module_name, len(plugin_module.plugins))
            self._modules.append(plugin_module)

    #
    # Properties
    #

    @property
    def modules(self) -> List[EZPluginModule]:
        """
        List of :class:`~EZPluginModule` modules loaded.

        Returns
        -------
        List[:class:`~ezplugins.plugin_module.EZPluginModule`] :
            Modules loaded during the course of finding plugins.

        """

        return self._modules

    @property
    def plugins(self) -> List[EZPlugin]:
        """
        Return a list of plugins loaded in all modules.

        Returns
        -------
        List[:class:`~ezplugins.plugin.EZPlugin`] :
            List of all plugins loaded.

        """

        plugins = []
        for module in self.modules:
            # Add plugins to our list
            plugins.extend(module.plugins)

        return plugins
