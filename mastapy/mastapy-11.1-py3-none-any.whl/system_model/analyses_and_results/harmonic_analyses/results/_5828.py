'''_5828.py

ResultLocationSelectionGroups
'''


from typing import List

from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.analyses_and_results.harmonic_analyses.results import _5827
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_RESULT_LOCATION_SELECTION_GROUPS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Results', 'ResultLocationSelectionGroups')


__docformat__ = 'restructuredtext en'
__all__ = ('ResultLocationSelectionGroups',)


class ResultLocationSelectionGroups(_0.APIBase):
    '''ResultLocationSelectionGroups

    This is a mastapy class.
    '''

    TYPE = _RESULT_LOCATION_SELECTION_GROUPS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ResultLocationSelectionGroups.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def select_result_location_group(self) -> 'list_with_selected_item.ListWithSelectedItem_ResultLocationSelectionGroup':
        '''list_with_selected_item.ListWithSelectedItem_ResultLocationSelectionGroup: 'SelectResultLocationGroup' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_ResultLocationSelectionGroup)(self.wrapped.SelectResultLocationGroup) if self.wrapped.SelectResultLocationGroup is not None else None

    @select_result_location_group.setter
    def select_result_location_group(self, value: 'list_with_selected_item.ListWithSelectedItem_ResultLocationSelectionGroup.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_ResultLocationSelectionGroup.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_ResultLocationSelectionGroup.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SelectResultLocationGroup = value

    @property
    def display_location_selection(self) -> 'ResultLocationSelectionGroups.DisplayLocationSelectionOption':
        '''DisplayLocationSelectionOption: 'DisplayLocationSelection' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.DisplayLocationSelection)
        return constructor.new(ResultLocationSelectionGroups.DisplayLocationSelectionOption)(value) if value is not None else None

    @display_location_selection.setter
    def display_location_selection(self, value: 'ResultLocationSelectionGroups.DisplayLocationSelectionOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.DisplayLocationSelection = value

    @property
    def selected_result_location_group(self) -> '_5827.ResultLocationSelectionGroup':
        '''ResultLocationSelectionGroup: 'SelectedResultLocationGroup' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5827.ResultLocationSelectionGroup)(self.wrapped.SelectedResultLocationGroup) if self.wrapped.SelectedResultLocationGroup is not None else None

    @property
    def result_location_groups(self) -> 'List[_5827.ResultLocationSelectionGroup]':
        '''List[ResultLocationSelectionGroup]: 'ResultLocationGroups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ResultLocationGroups, constructor.new(_5827.ResultLocationSelectionGroup))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def view_groups(self):
        ''' 'ViewGroups' is the original name of this method.'''

        self.wrapped.ViewGroups()

    def add_new_group(self):
        ''' 'AddNewGroup' is the original name of this method.'''

        self.wrapped.AddNewGroup()

    def remove_groups(self):
        ''' 'RemoveGroups' is the original name of this method.'''

        self.wrapped.RemoveGroups()

    def output_default_report_to(self, file_path: 'str'):
        ''' 'OutputDefaultReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputDefaultReportTo(file_path if file_path else '')

    def get_default_report_with_encoded_images(self) -> 'str':
        ''' 'GetDefaultReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetDefaultReportWithEncodedImages()
        return method_result

    def output_active_report_to(self, file_path: 'str'):
        ''' 'OutputActiveReportTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportTo(file_path if file_path else '')

    def output_active_report_as_text_to(self, file_path: 'str'):
        ''' 'OutputActiveReportAsTextTo' is the original name of this method.

        Args:
            file_path (str)
        '''

        file_path = str(file_path)
        self.wrapped.OutputActiveReportAsTextTo(file_path if file_path else '')

    def get_active_report_with_encoded_images(self) -> 'str':
        ''' 'GetActiveReportWithEncodedImages' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.GetActiveReportWithEncodedImages()
        return method_result

    def output_named_report_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportTo(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_masta_report(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsMastaReport' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsMastaReport(report_name if report_name else '', file_path if file_path else '')

    def output_named_report_as_text_to(self, report_name: 'str', file_path: 'str'):
        ''' 'OutputNamedReportAsTextTo' is the original name of this method.

        Args:
            report_name (str)
            file_path (str)
        '''

        report_name = str(report_name)
        file_path = str(file_path)
        self.wrapped.OutputNamedReportAsTextTo(report_name if report_name else '', file_path if file_path else '')

    def get_named_report_with_encoded_images(self, report_name: 'str') -> 'str':
        ''' 'GetNamedReportWithEncodedImages' is the original name of this method.

        Args:
            report_name (str)

        Returns:
            str
        '''

        report_name = str(report_name)
        method_result = self.wrapped.GetNamedReportWithEncodedImages(report_name if report_name else '')
        return method_result
