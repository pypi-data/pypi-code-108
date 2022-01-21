'''_1043.py

FinishStockType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FINISH_STOCK_TYPE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.ThicknessStockAndBacklash', 'FinishStockType')


__docformat__ = 'restructuredtext en'
__all__ = ('FinishStockType',)


class FinishStockType(Enum):
    '''FinishStockType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FINISH_STOCK_TYPE

    __hash__ = None

    NONE = 0
    SINGLE_VALUE = 1
    TOLERANCED_VALUE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FinishStockType.__setattr__ = __enum_setattr
FinishStockType.__delattr__ = __enum_delattr
