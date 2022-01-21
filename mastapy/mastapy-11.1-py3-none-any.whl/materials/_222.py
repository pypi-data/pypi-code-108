'''_222.py

DensitySpecificationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DENSITY_SPECIFICATION_METHOD = python_net_import('SMT.MastaAPI.Materials', 'DensitySpecificationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('DensitySpecificationMethod',)


class DensitySpecificationMethod(Enum):
    '''DensitySpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DENSITY_SPECIFICATION_METHOD

    __hash__ = None

    TEMPERATURE_INDEPENDENT_VALUE = 0
    TEMPERATURE_AND_VALUE_AT_TEMPERATURE_SPECIFIED = 1
    USER_SPECIFIED_VS_TEMPERATURE = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DensitySpecificationMethod.__setattr__ = __enum_setattr
DensitySpecificationMethod.__delattr__ = __enum_delattr
