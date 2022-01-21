'''_1244.py

CalculationMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CALCULATION_METHODS = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.InterferenceFits', 'CalculationMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('CalculationMethods',)


class CalculationMethods(Enum):
    '''CalculationMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CALCULATION_METHODS

    __hash__ = None

    SPECIFY_PRESSURE = 0
    SPECIFY_INTERFERENCE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CalculationMethods.__setattr__ = __enum_setattr
CalculationMethods.__delattr__ = __enum_delattr
