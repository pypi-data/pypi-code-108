'''_1637.py

BearingRow
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_ROW = python_net_import('SMT.MastaAPI.Bearings', 'BearingRow')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingRow',)


class BearingRow(Enum):
    '''BearingRow

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_ROW

    __hash__ = None

    LEFT = 0
    RIGHT = 1
    SINGLE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingRow.__setattr__ = __enum_setattr
BearingRow.__delattr__ = __enum_delattr
