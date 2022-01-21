'''_4079.py

DesignOfExperimentsVariableSetter
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4080
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DESIGN_OF_EXPERIMENTS_VARIABLE_SETTER = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'DesignOfExperimentsVariableSetter')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignOfExperimentsVariableSetter',)


class DesignOfExperimentsVariableSetter(_0.APIBase):
    '''DesignOfExperimentsVariableSetter

    This is a mastapy class.
    '''

    TYPE = _DESIGN_OF_EXPERIMENTS_VARIABLE_SETTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignOfExperimentsVariableSetter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_values(self) -> 'int':
        '''int: 'NumberOfValues' is the original name of this property.'''

        return self.wrapped.NumberOfValues

    @number_of_values.setter
    def number_of_values(self, value: 'int'):
        self.wrapped.NumberOfValues = int(value) if value else 0

    @property
    def define_using_range(self) -> 'bool':
        '''bool: 'DefineUsingRange' is the original name of this property.'''

        return self.wrapped.DefineUsingRange

    @define_using_range.setter
    def define_using_range(self, value: 'bool'):
        self.wrapped.DefineUsingRange = bool(value) if value else False

    @property
    def value_specification_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_DoeValueSpecificationOption':
        '''enum_with_selected_value.EnumWithSelectedValue_DoeValueSpecificationOption: 'ValueSpecificationType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_DoeValueSpecificationOption.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ValueSpecificationType, value) if self.wrapped.ValueSpecificationType is not None else None

    @value_specification_type.setter
    def value_specification_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_DoeValueSpecificationOption.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_DoeValueSpecificationOption.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ValueSpecificationType = value

    @property
    def current_design_value(self) -> 'float':
        '''float: 'CurrentDesignValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurrentDesignValue

    @property
    def start_value(self) -> 'float':
        '''float: 'StartValue' is the original name of this property.'''

        return self.wrapped.StartValue

    @start_value.setter
    def start_value(self, value: 'float'):
        self.wrapped.StartValue = float(value) if value else 0.0

    @property
    def end_value(self) -> 'float':
        '''float: 'EndValue' is the original name of this property.'''

        return self.wrapped.EndValue

    @end_value.setter
    def end_value(self, value: 'float'):
        self.wrapped.EndValue = float(value) if value else 0.0

    @property
    def value(self) -> 'float':
        '''float: 'Value' is the original name of this property.'''

        return self.wrapped.Value

    @value.setter
    def value(self, value: 'float'):
        self.wrapped.Value = float(value) if value else 0.0

    @property
    def integer_start_value(self) -> 'int':
        '''int: 'IntegerStartValue' is the original name of this property.'''

        return self.wrapped.IntegerStartValue

    @integer_start_value.setter
    def integer_start_value(self, value: 'int'):
        self.wrapped.IntegerStartValue = int(value) if value else 0

    @property
    def integer_end_value(self) -> 'int':
        '''int: 'IntegerEndValue' is the original name of this property.'''

        return self.wrapped.IntegerEndValue

    @integer_end_value.setter
    def integer_end_value(self, value: 'int'):
        self.wrapped.IntegerEndValue = int(value) if value else 0

    @property
    def integer_value(self) -> 'int':
        '''int: 'IntegerValue' is the original name of this property.'''

        return self.wrapped.IntegerValue

    @integer_value.setter
    def integer_value(self, value: 'int'):
        self.wrapped.IntegerValue = int(value) if value else 0

    @property
    def mean_value(self) -> 'float':
        '''float: 'MeanValue' is the original name of this property.'''

        return self.wrapped.MeanValue

    @mean_value.setter
    def mean_value(self, value: 'float'):
        self.wrapped.MeanValue = float(value) if value else 0.0

    @property
    def standard_deviation(self) -> 'float':
        '''float: 'StandardDeviation' is the original name of this property.'''

        return self.wrapped.StandardDeviation

    @standard_deviation.setter
    def standard_deviation(self, value: 'float'):
        self.wrapped.StandardDeviation = float(value) if value else 0.0

    @property
    def unit(self) -> 'str':
        '''str: 'Unit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Unit

    @property
    def start_value_in_si_units(self) -> 'float':
        '''float: 'StartValueInSIUnits' is the original name of this property.'''

        return self.wrapped.StartValueInSIUnits

    @start_value_in_si_units.setter
    def start_value_in_si_units(self, value: 'float'):
        self.wrapped.StartValueInSIUnits = float(value) if value else 0.0

    @property
    def end_value_in_si_units(self) -> 'float':
        '''float: 'EndValueInSIUnits' is the original name of this property.'''

        return self.wrapped.EndValueInSIUnits

    @end_value_in_si_units.setter
    def end_value_in_si_units(self, value: 'float'):
        self.wrapped.EndValueInSIUnits = float(value) if value else 0.0

    @property
    def value_in_si_units(self) -> 'float':
        '''float: 'ValueInSIUnits' is the original name of this property.'''

        return self.wrapped.ValueInSIUnits

    @value_in_si_units.setter
    def value_in_si_units(self, value: 'float'):
        self.wrapped.ValueInSIUnits = float(value) if value else 0.0

    @property
    def integer_start_value_in_si_units(self) -> 'int':
        '''int: 'IntegerStartValueInSIUnits' is the original name of this property.'''

        return self.wrapped.IntegerStartValueInSIUnits

    @integer_start_value_in_si_units.setter
    def integer_start_value_in_si_units(self, value: 'int'):
        self.wrapped.IntegerStartValueInSIUnits = int(value) if value else 0

    @property
    def integer_end_value_in_si_units(self) -> 'int':
        '''int: 'IntegerEndValueInSIUnits' is the original name of this property.'''

        return self.wrapped.IntegerEndValueInSIUnits

    @integer_end_value_in_si_units.setter
    def integer_end_value_in_si_units(self, value: 'int'):
        self.wrapped.IntegerEndValueInSIUnits = int(value) if value else 0

    @property
    def integer_value_in_si_units(self) -> 'int':
        '''int: 'IntegerValueInSIUnits' is the original name of this property.'''

        return self.wrapped.IntegerValueInSIUnits

    @integer_value_in_si_units.setter
    def integer_value_in_si_units(self, value: 'int'):
        self.wrapped.IntegerValueInSIUnits = int(value) if value else 0

    @property
    def mean_value_in_si_units(self) -> 'float':
        '''float: 'MeanValueInSIUnits' is the original name of this property.'''

        return self.wrapped.MeanValueInSIUnits

    @mean_value_in_si_units.setter
    def mean_value_in_si_units(self, value: 'float'):
        self.wrapped.MeanValueInSIUnits = float(value) if value else 0.0

    @property
    def standard_deviation_in_si_units(self) -> 'float':
        '''float: 'StandardDeviationInSIUnits' is the original name of this property.'''

        return self.wrapped.StandardDeviationInSIUnits

    @standard_deviation_in_si_units.setter
    def standard_deviation_in_si_units(self, value: 'float'):
        self.wrapped.StandardDeviationInSIUnits = float(value) if value else 0.0

    @property
    def doe_variable_values_in_si_units(self) -> 'List[float]':
        '''List[float]: 'DOEVariableValuesInSIUnits' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.DOEVariableValuesInSIUnits, float)
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def set_values(self, values: 'List[float]'):
        ''' 'SetValues' is the original name of this method.

        Args:
            values (List[float])
        '''

        values = conversion.mp_to_pn_list_float(values)
        self.wrapped.SetValues(values)

    def set_values_in_si_units(self, values: 'List[float]'):
        ''' 'SetValuesInSIUnits' is the original name of this method.

        Args:
            values (List[float])
        '''

        values = conversion.mp_to_pn_list_float(values)
        self.wrapped.SetValuesInSIUnits(values)

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
