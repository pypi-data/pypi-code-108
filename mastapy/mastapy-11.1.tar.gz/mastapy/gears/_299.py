'''_299.py

Hand
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HAND = python_net_import('SMT.MastaAPI.Gears', 'Hand')


__docformat__ = 'restructuredtext en'
__all__ = ('Hand',)


class Hand(Enum):
    '''Hand

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HAND

    __hash__ = None

    LEFT = 0
    RIGHT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


Hand.__setattr__ = __enum_setattr
Hand.__delattr__ = __enum_delattr
