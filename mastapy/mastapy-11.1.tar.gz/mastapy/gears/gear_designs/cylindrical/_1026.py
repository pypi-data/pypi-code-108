'''_1026.py

ScuffingTemperatureMethodsAGMA
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SCUFFING_TEMPERATURE_METHODS_AGMA = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'ScuffingTemperatureMethodsAGMA')


__docformat__ = 'restructuredtext en'
__all__ = ('ScuffingTemperatureMethodsAGMA',)


class ScuffingTemperatureMethodsAGMA(Enum):
    '''ScuffingTemperatureMethodsAGMA

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SCUFFING_TEMPERATURE_METHODS_AGMA

    __hash__ = None

    USER_INPUT = 0
    FROM_TEST_GEARS = 1
    FROM_LUBRICANT_VISCOSITY = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


ScuffingTemperatureMethodsAGMA.__setattr__ = __enum_setattr
ScuffingTemperatureMethodsAGMA.__delattr__ = __enum_delattr
