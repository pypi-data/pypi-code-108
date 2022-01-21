'''_5744.py

HarmonicAnalysisExportOptions
'''


from typing import List, Generic, TypeVar

from mastapy._internal.implicit import list_with_selected_item, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.math_utility import _1305
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5727
from mastapy.utility.units_and_measurements import _1403
from mastapy import _0
from mastapy.system_model.part_model import _2209
from mastapy._internal.python_net import python_net_import

_HARMONIC_ANALYSIS_EXPORT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses', 'HarmonicAnalysisExportOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicAnalysisExportOptions',)


TPartAnalysis = TypeVar('TPartAnalysis')
TPart = TypeVar('TPart', bound='_2209.Part')


class HarmonicAnalysisExportOptions(_0.APIBase, Generic[TPartAnalysis, TPart]):
    '''HarmonicAnalysisExportOptions

    This is a mastapy class.

    Generic Types:
        TPartAnalysis
        TPart
    '''

    TYPE = _HARMONIC_ANALYSIS_EXPORT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicAnalysisExportOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetary_duplicate_to_export(self) -> 'list_with_selected_item.ListWithSelectedItem_TPartAnalysis':
        '''list_with_selected_item.ListWithSelectedItem_TPartAnalysis: 'PlanetaryDuplicateToExport' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_TPartAnalysis)(self.wrapped.PlanetaryDuplicateToExport) if self.wrapped.PlanetaryDuplicateToExport is not None else None

    @planetary_duplicate_to_export.setter
    def planetary_duplicate_to_export(self, value: 'list_with_selected_item.ListWithSelectedItem_TPartAnalysis.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_TPartAnalysis.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_TPartAnalysis.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.PlanetaryDuplicateToExport = value

    @property
    def type_of_result_to_export(self) -> 'enum_with_selected_value.EnumWithSelectedValue_DynamicsResponseType':
        '''enum_with_selected_value.EnumWithSelectedValue_DynamicsResponseType: 'TypeOfResultToExport' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_DynamicsResponseType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.TypeOfResultToExport, value) if self.wrapped.TypeOfResultToExport is not None else None

    @type_of_result_to_export.setter
    def type_of_result_to_export(self, value: 'enum_with_selected_value.EnumWithSelectedValue_DynamicsResponseType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_DynamicsResponseType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.TypeOfResultToExport = value

    @property
    def export_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ExportOutputType':
        '''enum_with_selected_value.EnumWithSelectedValue_ExportOutputType: 'ExportType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ExportOutputType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ExportType, value) if self.wrapped.ExportType is not None else None

    @export_type.setter
    def export_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ExportOutputType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ExportOutputType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ExportType = value

    @property
    def distance_units_for_export(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'DistanceUnitsForExport' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.DistanceUnitsForExport) if self.wrapped.DistanceUnitsForExport is not None else None

    @distance_units_for_export.setter
    def distance_units_for_export(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.DistanceUnitsForExport = value

    @property
    def status_message_for_export(self) -> 'str':
        '''str: 'StatusMessageForExport' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StatusMessageForExport

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def export_results(self):
        ''' 'ExportResults' is the original name of this method.'''

        self.wrapped.ExportResults()

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
