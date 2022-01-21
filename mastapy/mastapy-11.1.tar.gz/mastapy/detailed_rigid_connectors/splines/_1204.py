'''_1204.py

PressureAngleTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_PRESSURE_ANGLE_TYPES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'PressureAngleTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('PressureAngleTypes',)


class PressureAngleTypes(Enum):
    '''PressureAngleTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _PRESSURE_ANGLE_TYPES

    __hash__ = None

    _30 = 0
    _375 = 1
    _45 = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PressureAngleTypes.__setattr__ = __enum_setattr
PressureAngleTypes.__delattr__ = __enum_delattr
