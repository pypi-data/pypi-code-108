'''_1520.py

CadPageOrientation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CAD_PAGE_ORIENTATION = python_net_import('SMT.MastaAPI.Utility.Report', 'CadPageOrientation')


__docformat__ = 'restructuredtext en'
__all__ = ('CadPageOrientation',)


class CadPageOrientation(Enum):
    '''CadPageOrientation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CAD_PAGE_ORIENTATION

    __hash__ = None

    LANDSCAPE = 0
    PORTRAIT = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CadPageOrientation.__setattr__ = __enum_setattr
CadPageOrientation.__delattr__ = __enum_delattr
