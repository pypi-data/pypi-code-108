'''_1715.py

PreloadType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PRELOAD_TYPE = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'PreloadType')


__docformat__ = 'restructuredtext en'
__all__ = ('PreloadType',)


class PreloadType(Enum):
    '''PreloadType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PRELOAD_TYPE

    __hash__ = None

    NONE = 0
    SOLID_PRELOAD = 1
    SPRING_PRELOAD = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PreloadType.__setattr__ = __enum_setattr
PreloadType.__delattr__ = __enum_delattr
