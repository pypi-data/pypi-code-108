'''_1700.py

LoadedBallElementChartReporter
'''


from mastapy._internal.implicit import enum_with_selected_value
from mastapy.bearings.bearing_results import _1716
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import enum_with_selected_value_runtime, conversion, constructor
from mastapy.utility.report import _1529
from mastapy._internal.python_net import python_net_import

_LOADED_BALL_ELEMENT_CHART_REPORTER = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedBallElementChartReporter')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBallElementChartReporter',)


class LoadedBallElementChartReporter(_1529.CustomReportChart):
    '''LoadedBallElementChartReporter

    This is a mastapy class.
    '''

    TYPE = _LOADED_BALL_ELEMENT_CHART_REPORTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedBallElementChartReporter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def element_to_plot(self) -> 'enum_with_selected_value.EnumWithSelectedValue_LoadedBallElementPropertyType':
        '''enum_with_selected_value.EnumWithSelectedValue_LoadedBallElementPropertyType: 'ElementToPlot' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_LoadedBallElementPropertyType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ElementToPlot, value) if self.wrapped.ElementToPlot is not None else None

    @element_to_plot.setter
    def element_to_plot(self, value: 'enum_with_selected_value.EnumWithSelectedValue_LoadedBallElementPropertyType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LoadedBallElementPropertyType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ElementToPlot = value
