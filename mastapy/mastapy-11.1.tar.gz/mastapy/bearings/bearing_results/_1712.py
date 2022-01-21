'''_1712.py

LoadedRollerElementChartReporter
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1529
from mastapy._internal.python_net import python_net_import

_LOADED_ROLLER_ELEMENT_CHART_REPORTER = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedRollerElementChartReporter')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedRollerElementChartReporter',)


class LoadedRollerElementChartReporter(_1529.CustomReportChart):
    '''LoadedRollerElementChartReporter

    This is a mastapy class.
    '''

    TYPE = _LOADED_ROLLER_ELEMENT_CHART_REPORTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedRollerElementChartReporter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def only_show_roller_with_highest_load(self) -> 'bool':
        '''bool: 'OnlyShowRollerWithHighestLoad' is the original name of this property.'''

        return self.wrapped.OnlyShowRollerWithHighestLoad

    @only_show_roller_with_highest_load.setter
    def only_show_roller_with_highest_load(self, value: 'bool'):
        self.wrapped.OnlyShowRollerWithHighestLoad = bool(value) if value else False

    @property
    def start_y_axis_at_zero(self) -> 'bool':
        '''bool: 'StartYAxisAtZero' is the original name of this property.'''

        return self.wrapped.StartYAxisAtZero

    @start_y_axis_at_zero.setter
    def start_y_axis_at_zero(self, value: 'bool'):
        self.wrapped.StartYAxisAtZero = bool(value) if value else False
