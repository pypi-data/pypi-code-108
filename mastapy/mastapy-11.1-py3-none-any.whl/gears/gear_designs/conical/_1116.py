'''_1116.py

LoadDistributionFactorMethods
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_LOAD_DISTRIBUTION_FACTOR_METHODS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'LoadDistributionFactorMethods')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadDistributionFactorMethods',)


class LoadDistributionFactorMethods(Enum):
    '''LoadDistributionFactorMethods

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _LOAD_DISTRIBUTION_FACTOR_METHODS

    __hash__ = None

    CALCULATE_FROM_MISALIGNMENT = 0
    DETERMINED_FROM_APPLICATION_AND_MOUNTING = 1
    SPECIFIED = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


LoadDistributionFactorMethods.__setattr__ = __enum_setattr
LoadDistributionFactorMethods.__delattr__ = __enum_delattr
