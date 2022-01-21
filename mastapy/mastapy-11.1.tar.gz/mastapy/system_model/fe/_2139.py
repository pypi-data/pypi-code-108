'''_2139.py

LinkNodeSource
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LINK_NODE_SOURCE = python_net_import('SMT.MastaAPI.SystemModel.FE', 'LinkNodeSource')


__docformat__ = 'restructuredtext en'
__all__ = ('LinkNodeSource',)


class LinkNodeSource(Enum):
    '''LinkNodeSource

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LINK_NODE_SOURCE

    __hash__ = None

    EXISTING_CONDENSATION_NODE = 0
    CREATE_SINGLE_AXIAL_NODE = 1
    CREATE_NODES_AT_ANGLES = 2
    CREATE_FLEXIBLE_NODE_RING = 3
    NONE = 4
    USE_NODES_FROM_ANOTHER_LINK = 5
    CREATE_ONE_NODE_PER_TOOTH = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LinkNodeSource.__setattr__ = __enum_setattr
LinkNodeSource.__delattr__ = __enum_delattr
