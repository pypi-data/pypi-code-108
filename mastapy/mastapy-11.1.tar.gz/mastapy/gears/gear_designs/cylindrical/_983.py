'''_983.py

CylindricalGearProfileModifications
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_PROFILE_MODIFICATIONS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearProfileModifications')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearProfileModifications',)


class CylindricalGearProfileModifications(Enum):
    '''CylindricalGearProfileModifications

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CYLINDRICAL_GEAR_PROFILE_MODIFICATIONS

    __hash__ = None

    NONE = 0
    HIGH_LOAD = 1
    SMOOTH_MESHING = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CylindricalGearProfileModifications.__setattr__ = __enum_setattr
CylindricalGearProfileModifications.__delattr__ = __enum_delattr
