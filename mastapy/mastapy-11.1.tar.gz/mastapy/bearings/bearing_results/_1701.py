'''_1701.py

LoadedBearingChartReporter
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.utility.report import _1526
from mastapy._internal.python_net import python_net_import

_LOADED_BEARING_CHART_REPORTER = python_net_import('SMT.MastaAPI.Bearings.BearingResults', 'LoadedBearingChartReporter')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedBearingChartReporter',)


class LoadedBearingChartReporter(_1526.CustomImage):
    '''LoadedBearingChartReporter

    This is a mastapy class.
    '''

    TYPE = _LOADED_BEARING_CHART_REPORTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedBearingChartReporter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def property_(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'Property' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.Property) if self.wrapped.Property is not None else None

    @property_.setter
    def property_(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.Property = value
