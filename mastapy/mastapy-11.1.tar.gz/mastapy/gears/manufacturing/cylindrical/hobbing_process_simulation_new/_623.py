'''_623.py

CentreDistanceOffsetMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CENTRE_DISTANCE_OFFSET_METHOD = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'CentreDistanceOffsetMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('CentreDistanceOffsetMethod',)


class CentreDistanceOffsetMethod(Enum):
    '''CentreDistanceOffsetMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CENTRE_DISTANCE_OFFSET_METHOD

    __hash__ = None

    CONSTANT_CENTRE_DISTANCE_OFFSET = 0
    PARABOLIC_CURVE_FOR_CENTRE_DISTANCE_OFFSET = 1
    SPECIFIED_GEAR_LEAD_MODIFICATION = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CentreDistanceOffsetMethod.__setattr__ = __enum_setattr
CentreDistanceOffsetMethod.__delattr__ = __enum_delattr
