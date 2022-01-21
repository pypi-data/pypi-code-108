'''_1558.py

HeadingSize
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HEADING_SIZE = python_net_import('SMT.MastaAPI.Utility.Report', 'HeadingSize')


__docformat__ = 'restructuredtext en'
__all__ = ('HeadingSize',)


class HeadingSize(Enum):
    '''HeadingSize

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HEADING_SIZE

    __hash__ = None

    REGULAR = 0
    MEDIUM = 1
    LARGE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HeadingSize.__setattr__ = __enum_setattr
HeadingSize.__delattr__ = __enum_delattr
