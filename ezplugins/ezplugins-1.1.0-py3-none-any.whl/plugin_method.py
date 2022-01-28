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

"""EZPlugins plugin method class."""

from typing import Any, Callable


class EZPluginMethod:
    """
    Representation of a plugin method. This class is designed to be instantiated during plugin load.

    See :meth:`~ezplugins.manager.EZPluginManager.methods` for how to call plugin methods.

    Parameters
    ----------
    method : Callable[..., Any]
        Plugin method.

    """

    _method: Callable[..., Any]

    def __init__(self, method: Callable[..., Any]) -> None:
        """
        Representation of a plugin method. This class is designed to be instantiated during plugin load.

        See :meth:`ezplugins.manager.EZPluginManager.methods` for how to call plugin methods.

        Parameters
        ----------
        method : Callable[..., Any]
            Plugin method.

        """

        self._method = method  # type: ignore

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Run the method.

        Parameters
        ----------
        args : Any
            Arguments to pass.

        kwargs : Any
            Keyword arguments to pass.

        """
        return self.method(*args, **kwargs)

    @property
    def method(self) -> Callable[..., Any]:
        """
        Actual :class:`EZPlugin` method which can be called.

        Returns
        -------
        Callable[..., Any] :
            A callable.

        """
        return self._method

    @property
    def name(self) -> str:
        """
        Name of the EZPlugin method.

        Returns
        -------
        :class:`str` :
            :class:`EZPlugin` method name.

        """
        return self.method.__name__

    @property
    def order(self) -> int:
        """
        Order of execution of this EZPlugin method.

        Returns
        -------
        :class:`int` :
            Order of execution.

        """
        return int(getattr(self.method, "_ezplugin_order"))
