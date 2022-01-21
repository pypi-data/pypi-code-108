'''_402.py

ProfileCrowningSetting
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PROFILE_CROWNING_SETTING = python_net_import('SMT.MastaAPI.Gears.Rating.Iso10300', 'ProfileCrowningSetting')


__docformat__ = 'restructuredtext en'
__all__ = ('ProfileCrowningSetting',)


class ProfileCrowningSetting(Enum):
    '''ProfileCrowningSetting

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PROFILE_CROWNING_SETTING

    __hash__ = None

    PROFILE_CROWNING_LOW_AUTOMOTIVE_GEARS = 0
    PROFILE_CROWNING_HIGH_INDUSTRIAL_GEARS = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ProfileCrowningSetting.__setattr__ = __enum_setattr
ProfileCrowningSetting.__delattr__ = __enum_delattr
