'''_272.py

HeadingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HEADING_TYPE = python_net_import('SMT.MastaAPI.HTML', 'HeadingType')


__docformat__ = 'restructuredtext en'
__all__ = ('HeadingType',)


class HeadingType(Enum):
    '''HeadingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HEADING_TYPE

    __hash__ = None

    VERY_SMALL = 0
    REGULAR = 1
    MEDIUM = 2
    LARGE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HeadingType.__setattr__ = __enum_setattr
HeadingType.__delattr__ = __enum_delattr
