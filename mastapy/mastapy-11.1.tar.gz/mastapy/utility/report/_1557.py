'''_1557.py

FontWeight
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FONT_WEIGHT = python_net_import('SMT.MastaAPI.Utility.Report', 'FontWeight')


__docformat__ = 'restructuredtext en'
__all__ = ('FontWeight',)


class FontWeight(Enum):
    '''FontWeight

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FONT_WEIGHT

    __hash__ = None

    NORMAL = 0
    BOLD = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FontWeight.__setattr__ = __enum_setattr
FontWeight.__delattr__ = __enum_delattr
