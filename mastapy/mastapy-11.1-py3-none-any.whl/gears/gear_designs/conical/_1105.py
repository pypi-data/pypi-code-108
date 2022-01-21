'''_1105.py

ConicalManufactureMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONICAL_MANUFACTURE_METHODS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'ConicalManufactureMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalManufactureMethods',)


class ConicalManufactureMethods(Enum):
    '''ConicalManufactureMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONICAL_MANUFACTURE_METHODS

    __hash__ = None

    FORMATE_TILT = 0
    FORMATE_MODIFIED_ROLL = 1
    GENERATING_TILT = 2
    GENERATING_TILT_WITH_OFFSET = 3
    GENERATING_MODIFIED_ROLL = 4
    HELIXFORM = 5


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ConicalManufactureMethods.__setattr__ = __enum_setattr
ConicalManufactureMethods.__delattr__ = __enum_delattr
