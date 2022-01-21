'''_1716.py

LoadedBallElementPropertyType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOADED_BALL_ELEMENT_PROPERTY_TYPE = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedBallElementPropertyType')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBallElementPropertyType',)


class LoadedBallElementPropertyType(Enum):
    '''LoadedBallElementPropertyType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOADED_BALL_ELEMENT_PROPERTY_TYPE

    __hash__ = None

    ELEMENT_WITH_HIGHEST_SLIDING_SPEED = 0
    ELEMENT_WITH_HIGHEST_PRESSURE_VELOCITY = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LoadedBallElementPropertyType.__setattr__ = __enum_setattr
LoadedBallElementPropertyType.__delattr__ = __enum_delattr
