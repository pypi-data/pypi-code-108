'''_875.py

LargerOrSmaller
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LARGER_OR_SMALLER = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'LargerOrSmaller')


__docformat__ = 'restructuredtext en'
__all__ = ('LargerOrSmaller',)


class LargerOrSmaller(Enum):
    '''LargerOrSmaller

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LARGER_OR_SMALLER

    __hash__ = None

    LARGER_VALUES = 0
    SMALLER_VALUES = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LargerOrSmaller.__setattr__ = __enum_setattr
LargerOrSmaller.__delattr__ = __enum_delattr
