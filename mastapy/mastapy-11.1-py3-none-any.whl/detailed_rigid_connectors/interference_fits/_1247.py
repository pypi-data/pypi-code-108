'''_1247.py

StressRegions
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_STRESS_REGIONS = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.InterferenceFits', 'StressRegions')


__docformat__ = 'restructuredtext en'
__all__ = ('StressRegions',)


class StressRegions(Enum):
    '''StressRegions

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _STRESS_REGIONS

    __hash__ = None

    FULLY_ELASTIC = 0
    PLASTICELASTIC = 1
    FULLY_PLASTIC = 2


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


StressRegions.__setattr__ = __enum_setattr
StressRegions.__delattr__ = __enum_delattr
