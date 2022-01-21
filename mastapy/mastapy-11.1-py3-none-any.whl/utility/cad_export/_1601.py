'''_1601.py

StockDrawings
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_STOCK_DRAWINGS = python_net_import('SMT.MastaAPI.Utility.CadExport', 'StockDrawings')


__docformat__ = 'restructuredtext en'
__all__ = ('StockDrawings',)


class StockDrawings(Enum):
    '''StockDrawings

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _STOCK_DRAWINGS

    __hash__ = None

    GEAR_CHAMFER_DETAIL = 0
    RACK_WITH_SEMI_TOPPING = 1
    RACK_WITHOUT_SEMI_TOPPING = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


StockDrawings.__setattr__ = __enum_setattr
StockDrawings.__delattr__ = __enum_delattr
