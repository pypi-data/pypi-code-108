'''_1653.py

RollingBearingType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ROLLING_BEARING_TYPE = python_net_import('SMT.MastaAPI.Bearings', 'RollingBearingType')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingBearingType',)


class RollingBearingType(Enum):
    '''RollingBearingType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ROLLING_BEARING_TYPE

    __hash__ = None

    ALL = 0
    ANGULAR_CONTACT_BALL_BEARING = 1
    FOUR_POINT_CONTACT_BALL_BEARING = 2
    THREE_POINT_CONTACT_BALL_BEARING = 3
    DEEP_GROOVE_BALL_BEARING = 4
    CYLINDRICAL_ROLLER_BEARING = 5
    NEEDLE_ROLLER_BEARING = 6
    SPHERICAL_ROLLER_BEARING = 7
    TAPER_ROLLER_BEARING = 8
    AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING = 9
    SELF_ALIGNING_BALL_BEARING = 10
    TOROIDAL_ROLLER_BEARING = 11
    SPHERICAL_ROLLER_THRUST_BEARING = 12
    ASYMMETRIC_SPHERICAL_ROLLER_BEARING = 13
    AXIAL_THRUST_NEEDLE_ROLLER_BEARING = 14
    THRUST_BALL_BEARING = 15
    ANGULAR_CONTACT_THRUST_BALL_BEARING = 16
    CROSSED_ROLLER_BEARING = 17


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


RollingBearingType.__setattr__ = __enum_setattr
RollingBearingType.__delattr__ = __enum_delattr
