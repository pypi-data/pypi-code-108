'''_1672.py

RadialSpecificationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_RADIAL_SPECIFICATION_METHOD = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'RadialSpecificationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('RadialSpecificationMethod',)


class RadialSpecificationMethod(Enum):
    '''RadialSpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _RADIAL_SPECIFICATION_METHOD

    __hash__ = None

    X_AND_Y = 0
    IN_DIRECTION_OF_ECCENTRICITY = 1
    IN_OPPOSITE_DIRECTION_TO_ECCENTRICITY = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RadialSpecificationMethod.__setattr__ = __enum_setattr
RadialSpecificationMethod.__delattr__ = __enum_delattr
