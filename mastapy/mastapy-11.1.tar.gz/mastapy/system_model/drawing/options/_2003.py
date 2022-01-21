'''_2003.py

AdvancedTimeSteppingAnalysisForModulationModeViewOptions
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6728, _6729
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.part_model.gears import _2272
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_MODE_VIEW_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.Drawing.Options', 'AdvancedTimeSteppingAnalysisForModulationModeViewOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedTimeSteppingAnalysisForModulationModeViewOptions',)


class AdvancedTimeSteppingAnalysisForModulationModeViewOptions(_0.APIBase):
    '''AdvancedTimeSteppingAnalysisForModulationModeViewOptions

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_MODE_VIEW_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedTimeSteppingAnalysisForModulationModeViewOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def large_time_step(self) -> 'int':
        '''int: 'LargeTimeStep' is the original name of this property.'''

        return self.wrapped.LargeTimeStep

    @large_time_step.setter
    def large_time_step(self, value: 'int'):
        self.wrapped.LargeTimeStep = int(value) if value else 0

    @property
    def excitations_type(self) -> '_6728.AtsamExcitationsOrOthers':
        '''AtsamExcitationsOrOthers: 'ExcitationsType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ExcitationsType)
        return constructor.new(_6728.AtsamExcitationsOrOthers)(value) if value is not None else None

    @excitations_type.setter
    def excitations_type(self, value: '_6728.AtsamExcitationsOrOthers'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ExcitationsType = value

    @property
    def mode_view_options(self) -> '_6729.AtsamNaturalFrequencyViewOption':
        '''AtsamNaturalFrequencyViewOption: 'ModeViewOptions' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ModeViewOptions)
        return constructor.new(_6729.AtsamNaturalFrequencyViewOption)(value) if value is not None else None

    @mode_view_options.setter
    def mode_view_options(self, value: '_6729.AtsamNaturalFrequencyViewOption'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ModeViewOptions = value

    @property
    def gear_set(self) -> 'list_with_selected_item.ListWithSelectedItem_GearSet':
        '''list_with_selected_item.ListWithSelectedItem_GearSet: 'GearSet' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_GearSet)(self.wrapped.GearSet) if self.wrapped.GearSet is not None else None

    @gear_set.setter
    def gear_set(self, value: 'list_with_selected_item.ListWithSelectedItem_GearSet.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_GearSet.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_GearSet.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.GearSet = value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

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
