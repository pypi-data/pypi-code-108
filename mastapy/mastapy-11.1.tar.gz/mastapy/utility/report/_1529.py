'''_1529.py

CustomReportChart
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1542, _1530
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_CHART = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportChart')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportChart',)


class CustomReportChart(_1542.CustomReportMultiPropertyItem['_1530.CustomReportChartItem']):
    '''CustomReportChart

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_CHART

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportChart.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def height(self) -> 'int':
        '''int: 'Height' is the original name of this property.'''

        return self.wrapped.Height

    @height.setter
    def height(self, value: 'int'):
        self.wrapped.Height = int(value) if value else 0

    @property
    def width(self) -> 'int':
        '''int: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'int'):
        self.wrapped.Width = int(value) if value else 0
