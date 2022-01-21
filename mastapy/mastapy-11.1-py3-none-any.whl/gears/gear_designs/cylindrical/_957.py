'''_957.py

BasicRackProfiles
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BASIC_RACK_PROFILES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'BasicRackProfiles')


__docformat__ = 'restructuredtext en'
__all__ = ('BasicRackProfiles',)


class BasicRackProfiles(Enum):
    '''BasicRackProfiles

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BASIC_RACK_PROFILES

    __hash__ = None

    ISO_53_PROFILE_A = 0
    ISO_53_PROFILE_B = 1
    ISO_53_PROFILE_C = 2
    ISO_53_PROFILE_D = 3
    CUSTOM = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BasicRackProfiles.__setattr__ = __enum_setattr
BasicRackProfiles.__delattr__ = __enum_delattr
