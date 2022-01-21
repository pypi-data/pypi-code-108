'''_1521.py

CadPageSize
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CAD_PAGE_SIZE = python_net_import('SMT.MastaAPI.Utility.Report', 'CadPageSize')


__docformat__ = 'restructuredtext en'
__all__ = ('CadPageSize',)


class CadPageSize(Enum):
    '''CadPageSize

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CAD_PAGE_SIZE

    __hash__ = None

    _4A0 = 0
    _2A0 = 1
    A0 = 2
    A1 = 3
    A2 = 4
    A3 = 5
    A4 = 6
    A5 = 7
    A6 = 8
    A7 = 9
    A8 = 10
    A9 = 11
    A10 = 12
    LETTER = 13
    LEGAL = 14
    CUSTOM = 15


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CadPageSize.__setattr__ = __enum_setattr
CadPageSize.__delattr__ = __enum_delattr
