'''_1305.py

DynamicsResponseType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DYNAMICS_RESPONSE_TYPE = python_net_import('SMT.MastaAPI.MathUtility', 'DynamicsResponseType')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicsResponseType',)


class DynamicsResponseType(Enum):
    '''DynamicsResponseType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DYNAMICS_RESPONSE_TYPE

    __hash__ = None

    DISPLACEMENT = 0
    VELOCITY = 1
    ACCELERATION = 2
    FORCE = 3
    STRAIN_ENERGY = 4
    KINETIC_ENERGY = 5
    LINE_OF_ACTION_SEPARATION = 6
    DYNAMIC_MESH_FORCE = 7
    DYNAMIC_MESH_MOMENT = 8
    DYNAMIC_TE = 9
    DYNAMIC_TE_GEAR_A = 10
    DYNAMIC_TE_GEAR_B = 11
    DYNAMIC_MISALIGNMENT = 12
    DYNAMIC_MISALIGNMENT_GEAR_A = 13
    DYNAMIC_MISALIGNMENT_GEAR_B = 14
    ROOT_MEAN_SQUARED_NORMAL_DISPLACEMENT = 15
    ROOT_MEAN_SQUARED_NORMAL_VELOCITY = 16
    ROOT_MEAN_SQUARED_NORMAL_ACCELERATION = 17
    MAXIMUM_NORMAL_VELOCITY = 18
    AIRBORNE_SOUND_POWER = 19
    SOUND_INTENSITY = 20
    SOUND_PRESSURE = 21
    STATIC_TE = 22
    STATIC_MISALIGNMENT = 23


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DynamicsResponseType.__setattr__ = __enum_setattr
DynamicsResponseType.__delattr__ = __enum_delattr
