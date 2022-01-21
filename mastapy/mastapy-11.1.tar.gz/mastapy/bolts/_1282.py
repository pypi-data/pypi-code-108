'''_1282.py

StandardSizes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_STANDARD_SIZES = python_net_import('SMT.MastaAPI.Bolts', 'StandardSizes')


__docformat__ = 'restructuredtext en'
__all__ = ('StandardSizes',)


class StandardSizes(Enum):
    '''StandardSizes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _STANDARD_SIZES

    __hash__ = None

    NON_STANDARD_SIZE = 0
    M4 = 4
    M5 = 5
    M6 = 6
    M7 = 7
    M8 = 8
    M9 = 9
    M10 = 10
    M12 = 12
    M14 = 14
    M16 = 16
    M18 = 18
    M20 = 20
    M22 = 22
    M24 = 24
    M27 = 27
    M30 = 30
    M33 = 33
    M36 = 36
    M39 = 39


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


StandardSizes.__setattr__ = __enum_setattr
StandardSizes.__delattr__ = __enum_delattr
