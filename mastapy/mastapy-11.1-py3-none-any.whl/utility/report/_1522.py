'''_1522.py

CadTableBorderType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CAD_TABLE_BORDER_TYPE = python_net_import('SMT.MastaAPI.Utility.Report', 'CadTableBorderType')


__docformat__ = 'restructuredtext en'
__all__ = ('CadTableBorderType',)


class CadTableBorderType(Enum):
    '''CadTableBorderType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CAD_TABLE_BORDER_TYPE

    __hash__ = None

    SINGLE = 0
    DOUBLE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CadTableBorderType.__setattr__ = __enum_setattr
CadTableBorderType.__delattr__ = __enum_delattr
