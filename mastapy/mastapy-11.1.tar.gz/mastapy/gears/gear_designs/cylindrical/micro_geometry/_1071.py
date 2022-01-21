'''_1071.py

MicroGeometryLeadToleranceChartView
'''


from enum import Enum

from mastapy._internal.python_net import python_net_import

_MICRO_GEOMETRY_LEAD_TOLERANCE_CHART_VIEW = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'MicroGeometryLeadToleranceChartView')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryLeadToleranceChartView',)


class MicroGeometryLeadToleranceChartView(Enum):
    '''MicroGeometryLeadToleranceChartView

    This is a mastapy class.

    Note:
        This class is an Enum.
    '''

    @classmethod
    def type_(cls):
        return _MICRO_GEOMETRY_LEAD_TOLERANCE_CHART_VIEW

    __hash__ = None

    TIP_TO_ROOT_VIEW = 0
    ROOT_TO_TIP_VIEW = 1


def __enum_setattr(self, attr, value):
    raise AttributeError('Cannot set the attributes of an Enum.') from None


def __enum_delattr(self, attr):
    raise AttributeError('Cannot delete the attributes of an Enum.') from None


MicroGeometryLeadToleranceChartView.__setattr__ = __enum_setattr
MicroGeometryLeadToleranceChartView.__delattr__ = __enum_delattr
