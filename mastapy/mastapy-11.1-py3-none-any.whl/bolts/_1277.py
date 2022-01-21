'''_1277.py

HeadCapTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HEAD_CAP_TYPES = python_net_import('SMT.MastaAPI.Bolts', 'HeadCapTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('HeadCapTypes',)


class HeadCapTypes(Enum):
    '''HeadCapTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HEAD_CAP_TYPES

    __hash__ = None

    HEXAGONAL_HEAD = 0
    SOCKET_HEAD = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HeadCapTypes.__setattr__ = __enum_setattr
HeadCapTypes.__delattr__ = __enum_delattr
