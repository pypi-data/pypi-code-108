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

"""EZPlugins decorators."""

from typing import Callable, Optional, Type, TypeVar

EZPT = TypeVar("EZPT")


def ezplugin(cls: Type[EZPT]) -> Type[EZPT]:
    """
    Decorate a class as being a loadable plugin.

    Classes can be decorated like this::

        import ezplugins

        @ezplugins.ezplugin
        class MyPlugin:
            ...

    The result of using this decorator is the class is marked as being a :class:`~ezplugins.plugin.EZPlugin` plugin class that is
    instantiated during plugin load.

    Multiple plugin classes can be defined in the same file. The search for plugin classes is recursive.

    The only restriction relating to plugins is that the plugin package must be a valid Python package.

    Internal plugin names are set to the path of the module it is loaded from within the ``PYTHONPATH`` and suffixed with
    ``#ClassName``, in this case it would be ``package.path#MyPlugin``. This can be used to call a specific plugin. On a side note,
    to make things easier, plugins can also be called using ``#ClassName``, keep in mind though that one can have two classes with
    the same name in different modules.

    See the :func:`~ezplugin_metadata` decorator for specifying a plugin alias.

    """

    def decorator(cls: Type[EZPT]) -> Type[EZPT]:
        # Set class attribute
        setattr(cls, "_is_ezplugin", True)
        return cls

    return decorator(cls)


def ezplugin_metadata(*, alias: Optional[str] = None) -> Callable[[EZPT], EZPT]:
    """
    Decorate a class as being a loadable plugin with metadata. See :func:`~ezplugin` for more information.

    Classes can be decorated and additional metadata added like this::

        import ezplugins

        @ezplugins.ezplugin_metadata(alias="CoolPlugin")
        class MyPlugin:
            ...

    Parameters
    ----------
    alias : Optioanl[:class:`str`]
        Plugin class alias, used when one wants to call a specific plugin or set of plugins with a custom name.
        This makes it easy to specify a plugin name instead of using the fully qualified plugin name or class name. You can also
        specify the same alias for a number of plugins which will result in all of them being called when using that alias.

    """

    def decorator(cls: EZPT) -> EZPT:
        # Set function attribute
        setattr(cls, "_is_ezplugin", True)
        # Setup metadata if it exists
        if alias:
            setattr(cls, "_ezplugin_alias", alias)
        return cls

    return decorator


def ezplugin_method(*, order: int = 5000) -> Callable[[EZPT], EZPT]:
    """
    Decorate a class method as a runnable plugin method and to provide it with an optional ``order`` or execution.

    Plugin methods must be decorated, this allows EZPlugins to know that this method can be called. The result of using this
    decorator is the method will get additional attributes set which EZPlugins looks for when determining which methods can be run
    or not.

    An example of using this decorator can be found below::

        import ezplugins

        @ezplugins.ezplugin
        class MyPlugin:

            ...

            # Methods must be decorated in order to be called
            @ezplugins.ezplugin_method()
            def some_method(self, param1, param2):
                return f"{param1=}, {param2=}"

            # With an execution order...
            @ezplugins.ezplugin_method(order=1000)
            def some_method(self, param1, param2):
                return f"{param1=}, {param2=}"

    Parameters
    ----------
    order : :class:`int`
        Run order of method if multiple methods are being executed. Defaults to 5000. Methods are executed lowest to highest.

    """

    def decorator(func: EZPT) -> EZPT:
        # Set function attribute
        setattr(func, "_ezplugin_order", order)
        return func

    return decorator
