'''_5234.py

TorqueConverterLockupRule
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_LOCKUP_RULE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'TorqueConverterLockupRule')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterLockupRule',)


class TorqueConverterLockupRule(Enum):
    '''TorqueConverterLockupRule

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _TORQUE_CONVERTER_LOCKUP_RULE

    __hash__ = None

    SPECIFY_TIME = 0
    SPEED_RATIO_AND_VEHICLE_SPEED = 1
    PRESSURE_VS_TIME = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


TorqueConverterLockupRule.__setattr__ = __enum_setattr
TorqueConverterLockupRule.__delattr__ = __enum_delattr
