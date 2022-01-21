'''_6723.py

TorqueValuesObtainedFrom
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TORQUE_VALUES_OBTAINED_FROM = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'TorqueValuesObtainedFrom')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueValuesObtainedFrom',)


class TorqueValuesObtainedFrom(Enum):
    '''TorqueValuesObtainedFrom

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TORQUE_VALUES_OBTAINED_FROM

    __hash__ = None

    BIN_CENTRES = 0
    LARGEST_MAGNITUDE = 1
    AVERAGE_OF_BIN_CONTENTS = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TorqueValuesObtainedFrom.__setattr__ = __enum_setattr
TorqueValuesObtainedFrom.__delattr__ = __enum_delattr
