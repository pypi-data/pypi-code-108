'''_1962.py

PowerLoadInputTorqueSpecificationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_POWER_LOAD_INPUT_TORQUE_SPECIFICATION_METHOD = python_net_import('SMT.MastaAPI.SystemModel', 'PowerLoadInputTorqueSpecificationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadInputTorqueSpecificationMethod',)


class PowerLoadInputTorqueSpecificationMethod(Enum):
    '''PowerLoadInputTorqueSpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _POWER_LOAD_INPUT_TORQUE_SPECIFICATION_METHOD

    __hash__ = None

    CONSTANT_TORQUE = 0
    ELECTRIC_MACHINE_HARMONIC_LOAD_DATA = 1
    TORQUE_VS_TIME = 2
    ENGINE_SPEED_TORQUE_CURVE = 3
    PID_CONTROL = 4
    TORQUE_VS_ANGLE = 5
    TORQUE_VS_ANGLE_AND_SPEED = 6
    SPEED_VS_TIME = 7


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PowerLoadInputTorqueSpecificationMethod.__setattr__ = __enum_setattr
PowerLoadInputTorqueSpecificationMethod.__delattr__ = __enum_delattr
