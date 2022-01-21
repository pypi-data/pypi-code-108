'''_1008.py

HeatTreatmentType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HEAT_TREATMENT_TYPE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'HeatTreatmentType')


__docformat__ = 'restructuredtext en'
__all__ = ('HeatTreatmentType',)


class HeatTreatmentType(Enum):
    '''HeatTreatmentType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HEAT_TREATMENT_TYPE

    __hash__ = None

    CARBURIZING = 0
    NITRIDING = 1
    INDUCTION_OR_FLAME = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HeatTreatmentType.__setattr__ = __enum_setattr
HeatTreatmentType.__delattr__ = __enum_delattr
