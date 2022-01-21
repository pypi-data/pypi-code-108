'''_606.py

MicroGeometryDefinitionType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_DEFINITION_TYPE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.PlungeShaving', 'MicroGeometryDefinitionType')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryDefinitionType',)


class MicroGeometryDefinitionType(Enum):
    '''MicroGeometryDefinitionType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICRO_GEOMETRY_DEFINITION_TYPE

    __hash__ = None

    DESIGN_MODE_MICRO_GEOMETRY = 0
    MANUFACTURING_MODE_MICRO_GEOMETRY = 1
    DESIGN_MODE_MANUFACTURING_MODE_MICRO_GEOMETRY = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicroGeometryDefinitionType.__setattr__ = __enum_setattr
MicroGeometryDefinitionType.__delattr__ = __enum_delattr
