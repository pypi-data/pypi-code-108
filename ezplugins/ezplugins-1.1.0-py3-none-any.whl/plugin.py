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

"""EZPlugins plugin classes."""

from typing import List, Optional

from .plugin_method import EZPluginMethod


class EZPlugin:
    """
    Class that represents the instantiated plugin. This class is designed to be instantiated during plugin load.

    See :attr:`~EZPluginManager.plugins` for how to get a list of loaded plugins.

    Parameters
    ----------
    obj : :class:`object`
        Plugin object.

    """

    _obj: object
    _methods: List[EZPluginMethod]
    _name: str
    _path: str
    _fqn: str
    _alias: Optional[str]

    def __init__(self, obj: object):
        """
        Class that represents the instantiated plugin. This class is designed to be instantiated during plugin load.

        See :attr:`~EZPluginManager.plugins` for how to get a list of loaded plugins.

        Parameters
        ----------
        obj : :class:`object`
            Plugin object.

        """

        self._obj = obj
        self._methods = []
        self._name = f"#{self.obj.__class__.__name__}"
        self._path = f"{self.obj.__class__.__module__}"
        self._fqn = f"{self.path}{self.name}"
        self._alias = getattr(self.obj, "_ezplugin_alias", None)

        # Loop through all items in the object
        for attr_name in dir(self.obj):
            # Grab the item we found
            attr = getattr(self.obj, attr_name)
            # Check if its callable and it has an order, if so its a method we want
            if callable(attr) and getattr(attr, "_ezplugin_order", None):
                self._methods.append(EZPluginMethod(attr))

    #
    # Properties
    #

    @property
    def obj(self) -> object:
        """
        Plugin object. This is the actual instantiated plugin.

        Returns
        -------
        :class:`object` :
            Plugin object.

        """
        return self._obj

    @property
    def methods(self) -> List[EZPluginMethod]:
        """
        Methods that were designated as callable within an EZPlugin.

        Returns
        -------
        List[:class:`~plugin_method.EZPluginMethod`] :
            A list of callables.

        """
        return self._methods

    @property
    def name(self) -> str:
        """
        Plugin name. In this case the class name prefixed with a #.

        Returns
        -------
        :class:`str` :
            Plugin name. (class name prefixed with #)

        """
        return self._name

    @property
    def fqn(self) -> str:
        """
        Plugin fully qualified name. ie. The path+name concatenated together.

        Returns
        -------
        :class:`str` :
            Fully qualified plugin name.

        """
        return self._fqn

    @property
    def path(self) -> str:
        """
        Plugin path. This is the module path to the class. It does not include the class name.

        Returns
        -------
        :class:`str` :
            Plugin path.

        """
        return self._path

    @property
    def alias(self) -> Optional[str]:
        """
        Plugin alias. This is the plugin alias which was specified by decorator.

        Returns
        -------
        Optional[:class:`str`] :
            Plugin alias.

        """
        return self._alias
