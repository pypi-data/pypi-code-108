# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
import abc
import inspect
import typing as _t


class NodePlugin(abc.ABC):
    """
    Meta base class for node plugins.

    Nodes which use plugins should subclass NodePlugin and implement
    the abstract method to serve as a specific plugin base class used for a
    single node or a specific group of nodes.

    Example:

    class BobPlugin(NodePlugin):
        def plugin_base_name() -> _t.str:
            return 'Bob'


    class BobNode(Node):
        ...
        plugins = [BobPlugin]


    The BobPlugin class may not be abstract and only single inheritance is
    allowed. Plugins of type BobPlugin then need to directly subclass Bobplugin
    and may not be abstract.
    """
    @staticmethod
    @abc.abstractmethod
    def plugin_base_name() -> str:
        pass

    @classmethod
    def plugin_impl_name(cls) -> str:
        return cls.__name__

    @classmethod
    def is_plugin_base(cls):
        base = cls.plugin_base()
        if base:
            return base is cls
        return False

    @classmethod
    def plugin_base(cls):
        if issubclass(cls, NodePlugin) and not inspect.isabstract(cls):
            for mcls in reversed(cls.mro()):
                if issubclass(mcls, NodePlugin) and not inspect.isabstract(mcls):
                    return mcls
        return None

    @classmethod
    def is_plugin(cls):
        base = cls.plugin_base()
        if base:
            return base is not cls
        return False
        
