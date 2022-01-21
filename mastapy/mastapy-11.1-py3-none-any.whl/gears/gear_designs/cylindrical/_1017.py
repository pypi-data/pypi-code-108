'''_1017.py

MicroGeometryProfileConvention
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_PROFILE_CONVENTION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'MicroGeometryProfileConvention')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryProfileConvention',)


class MicroGeometryProfileConvention(Enum):
    '''MicroGeometryProfileConvention

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICRO_GEOMETRY_PROFILE_CONVENTION

    __hash__ = None

    MASTA_DEFAULT_MATERIAL = 0
    LDP = 1
    ISOAGMADIN = 2
    VDIVDE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicroGeometryProfileConvention.__setattr__ = __enum_setattr
MicroGeometryProfileConvention.__delattr__ = __enum_delattr
