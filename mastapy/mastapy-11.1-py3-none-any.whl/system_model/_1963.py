'''_1963.py

PowerLoadPIDControlSpeedInputType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_POWER_LOAD_PID_CONTROL_SPEED_INPUT_TYPE = python_net_import('SMT.MastaAPI.SystemModel', 'PowerLoadPIDControlSpeedInputType')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadPIDControlSpeedInputType',)


class PowerLoadPIDControlSpeedInputType(Enum):
    '''PowerLoadPIDControlSpeedInputType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _POWER_LOAD_PID_CONTROL_SPEED_INPUT_TYPE

    __hash__ = None

    CONSTANT_SPEED = 0
    SPEED_VS_TIME = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


PowerLoadPIDControlSpeedInputType.__setattr__ = __enum_setattr
PowerLoadPIDControlSpeedInputType.__delattr__ = __enum_delattr
