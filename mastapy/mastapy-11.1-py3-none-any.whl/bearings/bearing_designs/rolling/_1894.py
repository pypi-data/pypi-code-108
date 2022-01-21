'''_1894.py

BearingProtectionLevel
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_BEARING_PROTECTION_LEVEL = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'BearingProtectionLevel')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingProtectionLevel',)


class BearingProtectionLevel(Enum):
    '''BearingProtectionLevel

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _BEARING_PROTECTION_LEVEL

    __hash__ = None

    NONE = 0
    INTERNAL_GEOMETRY_HIDDEN = 1
    INTERNAL_GEOMETRY_AND_ADVANCED_BEARING_RESULTS_HIDDEN = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


BearingProtectionLevel.__setattr__ = __enum_setattr
BearingProtectionLevel.__delattr__ = __enum_delattr
