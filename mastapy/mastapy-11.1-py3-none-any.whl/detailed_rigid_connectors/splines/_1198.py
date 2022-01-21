'''_1198.py

HeatTreatmentTypes
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_HEAT_TREATMENT_TYPES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'HeatTreatmentTypes')


__docformat__ = 'restructuredtext en'
__all__ = ('HeatTreatmentTypes',)


class HeatTreatmentTypes(Enum):
    '''HeatTreatmentTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _HEAT_TREATMENT_TYPES

    __hash__ = None

    NO_HEAT_TREATMENT = 0
    QUENCHED_TEMPERED = 1
    SURFACE_HARDENED = 2
    NITRIDED = 3
    CARBURIZED = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


HeatTreatmentTypes.__setattr__ = __enum_setattr
HeatTreatmentTypes.__delattr__ = __enum_delattr
