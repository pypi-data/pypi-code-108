'''_1922.py

WidthSeries
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_WIDTH_SERIES = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'WidthSeries')


__docformat__ = 'restructuredtext en'
__all__ = ('WidthSeries',)


class WidthSeries(Enum):
    '''WidthSeries

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _WIDTH_SERIES

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


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


WidthSeries.__setattr__ = __enum_setattr
WidthSeries.__delattr__ = __enum_delattr
