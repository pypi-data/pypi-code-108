'''_1648.py

RollerBearingProfileTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROLLER_BEARING_PROFILE_TYPES = python_net_import('SMT.MastaAPI.Bearings', 'RollerBearingProfileTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('RollerBearingProfileTypes',)


class RollerBearingProfileTypes(Enum):
    '''RollerBearingProfileTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROLLER_BEARING_PROFILE_TYPES

    __hash__ = None

    NONE = 0
    LUNDBERG = 1
    DIN_LUNDBERG = 2
    CROWNED = 3
    JOHNS_GOHAR = 4
    USERSPECIFIED = 5
    CONICAL = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RollerBearingProfileTypes.__setattr__ = __enum_setattr
RollerBearingProfileTypes.__delattr__ = __enum_delattr
