'''_1655.py

SealLocation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SEAL_LOCATION = python_net_import('SMT.MastaAPI.Bearings', 'SealLocation')


__docformat__ = 'restructuredtext en'
__all__ = ('SealLocation',)


class SealLocation(Enum):
    '''SealLocation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SEAL_LOCATION

    __hash__ = None

    NONE = 0
    ONE_SIDE = 1
    BOTH_SIDES = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SealLocation.__setattr__ = __enum_setattr
SealLocation.__delattr__ = __enum_delattr
