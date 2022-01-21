'''_1194.py

DudleyEffectiveLengthApproximationOption
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DUDLEY_EFFECTIVE_LENGTH_APPROXIMATION_OPTION = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'DudleyEffectiveLengthApproximationOption')


__docformat__ = 'restructuredtext en'
__all__ = ('DudleyEffectiveLengthApproximationOption',)


class DudleyEffectiveLengthApproximationOption(Enum):
    '''DudleyEffectiveLengthApproximationOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DUDLEY_EFFECTIVE_LENGTH_APPROXIMATION_OPTION

    __hash__ = None

    FOR_MAXIMUM_MISALIGNMENT = 0
    FOR_MODERATE_MISALIGNMENT = 1
    FOR_FLEXIBLE_SPLINES = 2
    FOR_FIXED_SPLINES_WITH_HELIX_MODIFICATION = 3
    FOR_FIXED_SPLINES_WITHOUT_HELIX_MODIFICATION = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DudleyEffectiveLengthApproximationOption.__setattr__ = __enum_setattr
DudleyEffectiveLengthApproximationOption.__delattr__ = __enum_delattr
