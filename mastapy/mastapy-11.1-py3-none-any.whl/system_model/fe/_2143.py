'''_2143.py

NodeSelectionDepthOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_NODE_SELECTION_DEPTH_OPTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'NodeSelectionDepthOption')


__docformat__ = 'restructuredtext en'
__all__ = ('NodeSelectionDepthOption',)


class NodeSelectionDepthOption(Enum):
    '''NodeSelectionDepthOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _NODE_SELECTION_DEPTH_OPTION

    __hash__ = None

    SURFACE_NODES = 0
    SOLID_NODES = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


NodeSelectionDepthOption.__setattr__ = __enum_setattr
NodeSelectionDepthOption.__delattr__ = __enum_delattr
