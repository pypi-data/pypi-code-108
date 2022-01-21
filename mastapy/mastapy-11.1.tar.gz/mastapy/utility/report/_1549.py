'''_1549.py

CustomReportTabs
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.utility.report import _1538, _1548
from mastapy._internal.python_net import python_net_import

_CUSTOM_REPORT_TABS = python_net_import('SMT.MastaAPI.Utility.Report', 'CustomReportTabs')


__docformat__ = 'restructuredtext en'
__all__ = ('CustomReportTabs',)


class CustomReportTabs(_1538.CustomReportItemContainerCollection['_1548.CustomReportTab']):
    '''CustomReportTabs

    This is a mastapy class.
    '''

    TYPE = _CUSTOM_REPORT_TABS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CustomReportTabs.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def scroll_content(self) -> 'bool':
        '''bool: 'ScrollContent' is the original name of this property.'''

        return self.wrapped.ScrollContent

    @scroll_content.setter
    def scroll_content(self, value: 'bool'):
        self.wrapped.ScrollContent = bool(value) if value else False

    @property
    def is_main_report_item(self) -> 'bool':
        '''bool: 'IsMainReportItem' is the original name of this property.'''

        return self.wrapped.IsMainReportItem

    @is_main_report_item.setter
    def is_main_report_item(self, value: 'bool'):
        self.wrapped.IsMainReportItem = bool(value) if value else False

    @property
    def layout_orientation(self) -> 'CustomReportTabs.ReportLayoutOrientation':
        '''ReportLayoutOrientation: 'LayoutOrientation' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LayoutOrientation)
        return constructor.new(CustomReportTabs.ReportLayoutOrientation)(value) if value is not None else None

    @layout_orientation.setter
    def layout_orientation(self, value: 'CustomReportTabs.ReportLayoutOrientation'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LayoutOrientation = value

    @property
    def number_of_tabs(self) -> 'int':
        '''int: 'NumberOfTabs' is the original name of this property.'''

        return self.wrapped.NumberOfTabs

    @number_of_tabs.setter
    def number_of_tabs(self, value: 'int'):
        self.wrapped.NumberOfTabs = int(value) if value else 0
