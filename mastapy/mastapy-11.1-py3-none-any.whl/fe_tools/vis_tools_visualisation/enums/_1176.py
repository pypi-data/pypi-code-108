'''_1176.py

CoordinateSystemType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_COORDINATE_SYSTEM_TYPE = python_net_import('SMT.MastaAPI.FETools.VisToolsVisualisation.Enums', 'CoordinateSystemType')


__docformat__ = 'restructuredtext en'
__all__ = ('CoordinateSystemType',)


class CoordinateSystemType(Enum):
    '''CoordinateSystemType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _COORDINATE_SYSTEM_TYPE

    __hash__ = None

    CARTESIAN = 1
    CYLINDRICAL = 2
    SPHERICAL = 3
    SPHERICAL_ALTERNATE = 4
    TOROIDAL = 5
    CYLINDRICAL_ALTERNATE = 6


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CoordinateSystemType.__setattr__ = __enum_setattr
CoordinateSystemType.__delattr__ = __enum_delattr
