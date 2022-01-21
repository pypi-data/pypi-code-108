'''_210.py

AcousticRadiationEfficiencyInputType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_ACOUSTIC_RADIATION_EFFICIENCY_INPUT_TYPE = python_net_import('SMT.MastaAPI.Materials', 'AcousticRadiationEfficiencyInputType')


__docformat__ = 'restructuredtext en'
__all__ = ('AcousticRadiationEfficiencyInputType',)


class AcousticRadiationEfficiencyInputType(Enum):
    '''AcousticRadiationEfficiencyInputType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _ACOUSTIC_RADIATION_EFFICIENCY_INPUT_TYPE

    __hash__ = None

    SPECIFY_VALUES = 0
    SIMPLE_PARAMETRISED = 1
    UNITY = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


AcousticRadiationEfficiencyInputType.__setattr__ = __enum_setattr
AcousticRadiationEfficiencyInputType.__delattr__ = __enum_delattr
