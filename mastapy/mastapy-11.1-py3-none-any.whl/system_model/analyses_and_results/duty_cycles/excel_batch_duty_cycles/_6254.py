'''_6254.py

ExcelFileDetails
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable, list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility.units_and_measurements import _1403
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_EXCEL_FILE_DETAILS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DutyCycles.ExcelBatchDutyCycles', 'ExcelFileDetails')


__docformat__ = 'restructuredtext en'
__all__ = ('ExcelFileDetails',)


class ExcelFileDetails(_0.APIBase):
    '''ExcelFileDetails

    This is a mastapy class.
    '''

    TYPE = _EXCEL_FILE_DETAILS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExcelFileDetails.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def header_row(self) -> 'int':
        '''int: 'HeaderRow' is the original name of this property.'''

        return self.wrapped.HeaderRow

    @header_row.setter
    def header_row(self, value: 'int'):
        self.wrapped.HeaderRow = int(value) if value else 0

    @property
    def header_column(self) -> 'int':
        '''int: 'HeaderColumn' is the original name of this property.'''

        return self.wrapped.HeaderColumn

    @header_column.setter
    def header_column(self, value: 'int'):
        self.wrapped.HeaderColumn = int(value) if value else 0

    @property
    def first_data_row(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'FirstDataRow' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.FirstDataRow) if self.wrapped.FirstDataRow is not None else None

    @first_data_row.setter
    def first_data_row(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.FirstDataRow = value

    @property
    def first_data_column(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'FirstDataColumn' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.FirstDataColumn) if self.wrapped.FirstDataColumn is not None else None

    @first_data_column.setter
    def first_data_column(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.FirstDataColumn = value

    @property
    def specify_number_of_data_rows_and_columns(self) -> 'bool':
        '''bool: 'SpecifyNumberOfDataRowsAndColumns' is the original name of this property.'''

        return self.wrapped.SpecifyNumberOfDataRowsAndColumns

    @specify_number_of_data_rows_and_columns.setter
    def specify_number_of_data_rows_and_columns(self, value: 'bool'):
        self.wrapped.SpecifyNumberOfDataRowsAndColumns = bool(value) if value else False

    @property
    def number_of_data_rows(self) -> 'int':
        '''int: 'NumberOfDataRows' is the original name of this property.'''

        return self.wrapped.NumberOfDataRows

    @number_of_data_rows.setter
    def number_of_data_rows(self, value: 'int'):
        self.wrapped.NumberOfDataRows = int(value) if value else 0

    @property
    def number_of_data_columns(self) -> 'int':
        '''int: 'NumberOfDataColumns' is the original name of this property.'''

        return self.wrapped.NumberOfDataColumns

    @number_of_data_columns.setter
    def number_of_data_columns(self, value: 'int'):
        self.wrapped.NumberOfDataColumns = int(value) if value else 0

    @property
    def negate_speeds_and_torques(self) -> 'bool':
        '''bool: 'NegateSpeedsAndTorques' is the original name of this property.'''

        return self.wrapped.NegateSpeedsAndTorques

    @negate_speeds_and_torques.setter
    def negate_speeds_and_torques(self, value: 'bool'):
        self.wrapped.NegateSpeedsAndTorques = bool(value) if value else False

    @property
    def specify_duration(self) -> 'bool':
        '''bool: 'SpecifyDuration' is the original name of this property.'''

        return self.wrapped.SpecifyDuration

    @specify_duration.setter
    def specify_duration(self, value: 'bool'):
        self.wrapped.SpecifyDuration = bool(value) if value else False

    @property
    def speed_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'SpeedUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.SpeedUnit) if self.wrapped.SpeedUnit is not None else None

    @speed_unit.setter
    def speed_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SpeedUnit = value

    @property
    def torque_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'TorqueUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.TorqueUnit) if self.wrapped.TorqueUnit is not None else None

    @torque_unit.setter
    def torque_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.TorqueUnit = value

    @property
    def cycles_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'CyclesUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.CyclesUnit) if self.wrapped.CyclesUnit is not None else None

    @cycles_unit.setter
    def cycles_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.CyclesUnit = value

    @property
    def duration_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'DurationUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.DurationUnit) if self.wrapped.DurationUnit is not None else None

    @duration_unit.setter
    def duration_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.DurationUnit = value

    @property
    def ignore_sheet_names_containing(self) -> 'str':
        '''str: 'IgnoreSheetNamesContaining' is the original name of this property.'''

        return self.wrapped.IgnoreSheetNamesContaining

    @ignore_sheet_names_containing.setter
    def ignore_sheet_names_containing(self, value: 'str'):
        self.wrapped.IgnoreSheetNamesContaining = str(value) if value else ''

    @property
    def compress_load_cases(self) -> 'bool':
        '''bool: 'CompressLoadCases' is the original name of this property.'''

        return self.wrapped.CompressLoadCases

    @compress_load_cases.setter
    def compress_load_cases(self, value: 'bool'):
        self.wrapped.CompressLoadCases = bool(value) if value else False

    @property
    def combine_positive_and_negative_speeds(self) -> 'bool':
        '''bool: 'CombinePositiveAndNegativeSpeeds' is the original name of this property.'''

        return self.wrapped.CombinePositiveAndNegativeSpeeds

    @combine_positive_and_negative_speeds.setter
    def combine_positive_and_negative_speeds(self, value: 'bool'):
        self.wrapped.CombinePositiveAndNegativeSpeeds = bool(value) if value else False

    @property
    def show_zero_duration_speeds_and_torques(self) -> 'bool':
        '''bool: 'ShowZeroDurationSpeedsAndTorques' is the original name of this property.'''

        return self.wrapped.ShowZeroDurationSpeedsAndTorques

    @show_zero_duration_speeds_and_torques.setter
    def show_zero_duration_speeds_and_torques(self, value: 'bool'):
        self.wrapped.ShowZeroDurationSpeedsAndTorques = bool(value) if value else False

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
