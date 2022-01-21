'''_1618.py

CustomLineChart
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1529
from mastapy._internal.python_net import python_net_import

_CUSTOM_LINE_CHART = python_net_import('SMT.MastaAPI.UtilityGUI.Charts', 'CustomLineChart')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomLineChart',)


class CustomLineChart(_1529.CustomReportChart):
    '''CustomLineChart

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_LINE_CHART

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomLineChart.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def x_values(self):
        ''' 'XValues' is the original name of this method.'''

        self.wrapped.XValues()

    def y_values(self):
        ''' 'YValues' is the original name of this method.'''

        self.wrapped.YValues()
