'''_1209.py

SAETorqueCycles
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SAE_TORQUE_CYCLES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'SAETorqueCycles')


__docformat__ = 'restructuredtext en'
__all__ = ('SAETorqueCycles',)


class SAETorqueCycles(Enum):
    '''SAETorqueCycles

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SAE_TORQUE_CYCLES

    __hash__ = None

    _1000 = 3
    _10000 = 4
    _100000 = 5
    _1000000 = 6
    _10000000 = 7


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SAETorqueCycles.__setattr__ = __enum_setattr
SAETorqueCycles.__delattr__ = __enum_delattr
