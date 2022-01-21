'''_1966.py

RelativeOffsetOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RELATIVE_OFFSET_OPTION = python_net_import('SMT.MastaAPI.SystemModel', 'RelativeOffsetOption')


__docformat__ = 'restructuredtext en'
__all__ = ('RelativeOffsetOption',)


class RelativeOffsetOption(Enum):
    '''RelativeOffsetOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RELATIVE_OFFSET_OPTION

    __hash__ = None

    LEFT = 0
    CENTRE = 1
    RIGHT = 2
    SPECIFIED = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RelativeOffsetOption.__setattr__ = __enum_setattr
RelativeOffsetOption.__delattr__ = __enum_delattr
