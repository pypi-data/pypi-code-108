'''_284.py

CentreDistanceChangeMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CENTRE_DISTANCE_CHANGE_METHOD = python_net_import('SMT.MastaAPI.Gears', 'CentreDistanceChangeMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('CentreDistanceChangeMethod',)


class CentreDistanceChangeMethod(Enum):
    '''CentreDistanceChangeMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CENTRE_DISTANCE_CHANGE_METHOD

    __hash__ = None

    AUTOMATIC = 0
    MANUAL = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CentreDistanceChangeMethod.__setattr__ = __enum_setattr
CentreDistanceChangeMethod.__delattr__ = __enum_delattr
