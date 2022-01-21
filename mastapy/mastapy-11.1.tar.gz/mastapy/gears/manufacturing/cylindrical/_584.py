'''_584.py

CylindricalMftRoughingMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_MFT_ROUGHING_METHODS = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'CylindricalMftRoughingMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMftRoughingMethods',)


class CylindricalMftRoughingMethods(Enum):
    '''CylindricalMftRoughingMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CYLINDRICAL_MFT_ROUGHING_METHODS

    __hash__ = None

    HOBBING = 0
    SHAPING = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CylindricalMftRoughingMethods.__setattr__ = __enum_setattr
CylindricalMftRoughingMethods.__delattr__ = __enum_delattr
