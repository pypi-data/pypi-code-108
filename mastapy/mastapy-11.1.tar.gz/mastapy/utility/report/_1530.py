'''_1530.py

CustomReportChartItem
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1546
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_CHART_ITEM = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportChartItem')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportChartItem',)


class CustomReportChartItem(_1546.CustomReportPropertyItem):
    '''CustomReportChartItem

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_CHART_ITEM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportChartItem.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def has_marker(self) -> 'bool':
        '''bool: 'HasMarker' is the original name of this property.'''

        return self.wrapped.HasMarker

    @has_marker.setter
    def has_marker(self, value: 'bool'):
        self.wrapped.HasMarker = bool(value) if value else False
