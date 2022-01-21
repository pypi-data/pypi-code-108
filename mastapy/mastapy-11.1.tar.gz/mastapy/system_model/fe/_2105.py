'''_2105.py

BearingNodeOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_NODE_OPTION = python_net_import('SMT.MastaAPI.SystemModel.FE', 'BearingNodeOption')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingNodeOption',)


class BearingNodeOption(Enum):
    '''BearingNodeOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_NODE_OPTION

    __hash__ = None

    SINGLE_NODE_FOR_BEARING = 0
    NODE_PER_BEARING_ROW = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingNodeOption.__setattr__ = __enum_setattr
BearingNodeOption.__delattr__ = __enum_delattr
