'''_1356.py

SpecifyOptimisationInputAs
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SPECIFY_OPTIMISATION_INPUT_AS = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'SpecifyOptimisationInputAs')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecifyOptimisationInputAs',)


class SpecifyOptimisationInputAs(Enum):
    '''SpecifyOptimisationInputAs

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SPECIFY_OPTIMISATION_INPUT_AS

    __hash__ = None

    SYMMETRIC_DEVIATION_FROM_ORIGINAL_DESIGN_PERCENTAGE = 0
    ASYMMETRIC_DEVIATION_FROM_ORIGINAL_DESIGN_PERCENTAGE = 1
    SYMMETRIC_DEVIATION_FROM_ORIGINAL_DESIGN_ABSOLUTE = 2
    ASYMMETRIC_DEVIATION_FROM_ORIGINAL_DESIGN_ABSOLUTE = 3
    ABSOLUTE_RANGE = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SpecifyOptimisationInputAs.__setattr__ = __enum_setattr
SpecifyOptimisationInputAs.__delattr__ = __enum_delattr
