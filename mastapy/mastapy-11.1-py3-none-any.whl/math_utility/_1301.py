'''_1301.py

DataPrecision
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DATA_PRECISION = python_net_import('SMT.MastaAPI.MathUtility', 'DataPrecision')


__docformat__ = 'restructuredtext en'
__all__ = ('DataPrecision',)


class DataPrecision(Enum):
    '''DataPrecision

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DATA_PRECISION

    __hash__ = None

    SINGLE = 0
    DOUBLE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DataPrecision.__setattr__ = __enum_setattr
DataPrecision.__delattr__ = __enum_delattr
