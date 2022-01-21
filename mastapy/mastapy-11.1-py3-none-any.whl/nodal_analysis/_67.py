'''_67.py

IntegrationMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_INTEGRATION_METHOD = python_net_import('SMT.MastaAPI.NodalAnalysis', 'IntegrationMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('IntegrationMethod',)


class IntegrationMethod(Enum):
    '''IntegrationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _INTEGRATION_METHOD

    __hash__ = None

    NEWMARK = 0
    NEWMARK_ACCELERATION = 1
    WILSON_THETA = 2
    HHT = 3
    RUNGEKUTTA_45_EXPLICIT = 4
    SEMIIMPLICIT_EXTRAPOLATION_METHOD = 5
    BACKWARD_EULER_VELOCITY = 6
    BACKWARD_EULER_ACCELERATION = 7
    LOBATTO3A_ORDER_2 = 8
    LOBATTO3C_ORDER_2 = 9
    ROSENBROCK_43 = 10


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


IntegrationMethod.__setattr__ = __enum_setattr
IntegrationMethod.__delattr__ = __enum_delattr
