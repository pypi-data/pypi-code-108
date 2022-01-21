'''_1029.py

SpurGearLoadSharingCodes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SPUR_GEAR_LOAD_SHARING_CODES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'SpurGearLoadSharingCodes')


__docformat__ = 'restructuredtext en'
__all__ = ('SpurGearLoadSharingCodes',)


class SpurGearLoadSharingCodes(Enum):
    '''SpurGearLoadSharingCodes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SPUR_GEAR_LOAD_SHARING_CODES

    __hash__ = None

    LOAD_AT_HPSTC = 0
    LOAD_AT_TIP = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SpurGearLoadSharingCodes.__setattr__ = __enum_setattr
SpurGearLoadSharingCodes.__delattr__ = __enum_delattr
