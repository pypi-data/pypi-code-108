'''_53.py

DampingScalingTypeForInitialTransients
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_DAMPING_SCALING_TYPE_FOR_INITIAL_TRANSIENTS = python_net_import('SMT.MastaAPI.NodalAnalysis', 'DampingScalingTypeForInitialTransients')


__docformat__ = 'restructuredtext en'
__all__ = ('DampingScalingTypeForInitialTransients',)


class DampingScalingTypeForInitialTransients(Enum):
    '''DampingScalingTypeForInitialTransients

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _DAMPING_SCALING_TYPE_FOR_INITIAL_TRANSIENTS

    __hash__ = None

    NONE = 0
    LINEAR = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


DampingScalingTypeForInitialTransients.__setattr__ = __enum_setattr
DampingScalingTypeForInitialTransients.__delattr__ = __enum_delattr
