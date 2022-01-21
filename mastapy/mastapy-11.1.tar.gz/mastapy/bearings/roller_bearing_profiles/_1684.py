'''_1684.py

ProfileToFit
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PROFILE_TO_FIT = python_net_import('SMT.MastaAPI.Bearings.RollerBearingProfiles', 'ProfileToFit')


__docformat__ = 'restructuredtext en'
__all__ = ('ProfileToFit',)


class ProfileToFit(Enum):
    '''ProfileToFit

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PROFILE_TO_FIT

    __hash__ = None

    AUTO = 0
    QUADRATIC = 1
    DIN_LUNDBERG = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ProfileToFit.__setattr__ = __enum_setattr
ProfileToFit.__delattr__ = __enum_delattr
