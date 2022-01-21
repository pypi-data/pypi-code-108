'''_562.py

ManufactureRating
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MANUFACTURE_RATING = python_net_import('SMT.MastaAPI.Gears.Materials', 'ManufactureRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ManufactureRating',)


class ManufactureRating(Enum):
    '''ManufactureRating

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MANUFACTURE_RATING

    __hash__ = None

    _0 = 0
    _1 = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9
    _10 = 10


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ManufactureRating.__setattr__ = __enum_setattr
ManufactureRating.__delattr__ = __enum_delattr
