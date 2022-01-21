'''_5171.py

InertiaAdjustedLoadCasePeriodMethod
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_INERTIA_ADJUSTED_LOAD_CASE_PERIOD_METHOD = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'InertiaAdjustedLoadCasePeriodMethod')


__docformat__ = 'restructuredtext en'
__all__ = ('InertiaAdjustedLoadCasePeriodMethod',)


class InertiaAdjustedLoadCasePeriodMethod(Enum):
    '''InertiaAdjustedLoadCasePeriodMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _INERTIA_ADJUSTED_LOAD_CASE_PERIOD_METHOD

    __hash__ = None

    TIME_PERIOD = 0
    POWER_LOAD_ANGLE = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


InertiaAdjustedLoadCasePeriodMethod.__setattr__ = __enum_setattr
InertiaAdjustedLoadCasePeriodMethod.__delattr__ = __enum_delattr
