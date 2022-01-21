'''_1556.py

FontStyle
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_FONT_STYLE = python_net_import('SMT.MastaAPI.Utility.Report', 'FontStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('FontStyle',)


class FontStyle(Enum):
    '''FontStyle

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _FONT_STYLE

    __hash__ = None

    NORMAL = 0
    ITALIC = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


FontStyle.__setattr__ = __enum_setattr
FontStyle.__delattr__ = __enum_delattr
