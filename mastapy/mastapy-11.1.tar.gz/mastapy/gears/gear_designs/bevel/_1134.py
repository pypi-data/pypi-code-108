'''_1134.py

MachineCharacteristicAGMAKlingelnberg
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MACHINE_CHARACTERISTIC_AGMA_KLINGELNBERG = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'MachineCharacteristicAGMAKlingelnberg')


__docformat__ = 'restructuredtext en'
__all__ = ('MachineCharacteristicAGMAKlingelnberg',)


class MachineCharacteristicAGMAKlingelnberg(Enum):
    '''MachineCharacteristicAGMAKlingelnberg

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MACHINE_CHARACTERISTIC_AGMA_KLINGELNBERG

    __hash__ = None

    UNIFORM = 0
    LIGHT_SHOCK = 1
    MEDIUM_SHOCK = 2
    HEAVY_SHOCK = 3


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MachineCharacteristicAGMAKlingelnberg.__setattr__ = __enum_setattr
MachineCharacteristicAGMAKlingelnberg.__delattr__ = __enum_delattr
