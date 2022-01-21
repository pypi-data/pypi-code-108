'''_6695.py

TorqueRippleInputType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TORQUE_RIPPLE_INPUT_TYPE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'TorqueRippleInputType')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueRippleInputType',)


class TorqueRippleInputType(Enum):
    '''TorqueRippleInputType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TORQUE_RIPPLE_INPUT_TYPE

    __hash__ = None

    ROTOR_TORQUE_RIPPLE_TIME_SERIES = 0
    STATOR_TEETH_TANGENTIAL_LOADS = 1
    INDEPENDENT_ROTOR_TORQUE_RIPPLE_AND_STATOR_TEETH_TANGENTIAL_LOADS = 2
    CONSTANT_TORQUE_NO_TORQUE_RIPPLE = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TorqueRippleInputType.__setattr__ = __enum_setattr
TorqueRippleInputType.__delattr__ = __enum_delattr
