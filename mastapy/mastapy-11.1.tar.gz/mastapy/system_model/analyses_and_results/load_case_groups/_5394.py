'''_5394.py

SystemOptimiserGearSetOptimisation
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_SYSTEM_OPTIMISER_GEAR_SET_OPTIMISATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups', 'SystemOptimiserGearSetOptimisation')


__docformat__ = 'restructuredtext en'
__all__ = ('SystemOptimiserGearSetOptimisation',)


class SystemOptimiserGearSetOptimisation(Enum):
    '''SystemOptimiserGearSetOptimisation

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _SYSTEM_OPTIMISER_GEAR_SET_OPTIMISATION

    __hash__ = None

    NONE = 0
    FAST = 1
    FULL = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


SystemOptimiserGearSetOptimisation.__setattr__ = __enum_setattr
SystemOptimiserGearSetOptimisation.__delattr__ = __enum_delattr
