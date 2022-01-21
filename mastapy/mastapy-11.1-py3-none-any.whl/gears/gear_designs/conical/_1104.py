'''_1104.py

ConicalMachineSettingCalculationMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CONICAL_MACHINE_SETTING_CALCULATION_METHODS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'ConicalMachineSettingCalculationMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMachineSettingCalculationMethods',)


class ConicalMachineSettingCalculationMethods(Enum):
    '''ConicalMachineSettingCalculationMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CONICAL_MACHINE_SETTING_CALCULATION_METHODS

    __hash__ = None

    GLEASON = 0
    SMT = 1
    SPECIFIED = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ConicalMachineSettingCalculationMethods.__setattr__ = __enum_setattr
ConicalMachineSettingCalculationMethods.__delattr__ = __enum_delattr
