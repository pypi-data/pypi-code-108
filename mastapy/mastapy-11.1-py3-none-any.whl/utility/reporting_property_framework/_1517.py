'''_1517.py

CustomChartType
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_CUSTOM_CHART_TYPE = python_net_import('SMT.MastaAPI.Utility.ReportingPropertyFramework', 'CustomChartType')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomChartType',)


class CustomChartType(Enum):
    '''CustomChartType

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _CUSTOM_CHART_TYPE

    __hash__ = None

    BAR_CHART = 0
    LINE_CHART = 1
    POLAR_CHART = 2
    SCATTER_CHART = 3
    BAR_AND_LINE_CHART = 4


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


CustomChartType.__setattr__ = __enum_setattr
CustomChartType.__delattr__ = __enum_delattr
