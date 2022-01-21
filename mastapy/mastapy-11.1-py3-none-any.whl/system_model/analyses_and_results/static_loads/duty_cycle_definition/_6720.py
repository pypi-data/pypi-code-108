'''_6720.py

TimeSeriesImporter
'''


from typing import List

from mastapy.system_model.analyses_and_results.static_loads import _6625
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal.cast_exception import CastException
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.system_model.analyses_and_results.static_loads.duty_cycle_definition import (
    _6710, _6721, _6712, _6709,
    _6713, _6715, _6722, _6719,
    _6711, _6714, _6708
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility.file_access_helpers import _1586
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TIME_SERIES_IMPORTER = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'TimeSeriesImporter')


__docformat__ = 'restructuredtext en'
__all__ = ('TimeSeriesImporter',)


class TimeSeriesImporter(_0.APIBase):
    '''TimeSeriesImporter

    This is a mastapy class.
    '''

    TYPE = _TIME_SERIES_IMPORTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TimeSeriesImporter.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def import_type(self) -> '_6625.ImportType':
        '''ImportType: 'ImportType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ImportType)
        return constructor.new(_6625.ImportType)(value) if value is not None else None

    @import_type.setter
    def import_type(self, value: '_6625.ImportType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ImportType = value

    @property
    def number_of_data_files(self) -> 'int':
        '''int: 'NumberOfDataFiles' is the original name of this property.'''

        return self.wrapped.NumberOfDataFiles

    @number_of_data_files.setter
    def number_of_data_files(self, value: 'int'):
        self.wrapped.NumberOfDataFiles = int(value) if value else 0

    @property
    def specify_load_case_names(self) -> 'bool':
        '''bool: 'SpecifyLoadCaseNames' is the original name of this property.'''

        return self.wrapped.SpecifyLoadCaseNames

    @specify_load_case_names.setter
    def specify_load_case_names(self, value: 'bool'):
        self.wrapped.SpecifyLoadCaseNames = bool(value) if value else False

    @property
    def number_of_extra_points_for_ramp_sections(self) -> 'int':
        '''int: 'NumberOfExtraPointsForRampSections' is the original name of this property.'''

        return self.wrapped.NumberOfExtraPointsForRampSections

    @number_of_extra_points_for_ramp_sections.setter
    def number_of_extra_points_for_ramp_sections(self, value: 'int'):
        self.wrapped.NumberOfExtraPointsForRampSections = int(value) if value else 0

    @property
    def number_of_cycle_repeats(self) -> 'float':
        '''float: 'NumberOfCycleRepeats' is the original name of this property.'''

        return self.wrapped.NumberOfCycleRepeats

    @number_of_cycle_repeats.setter
    def number_of_cycle_repeats(self, value: 'float'):
        self.wrapped.NumberOfCycleRepeats = float(value) if value else 0.0

    @property
    def number_of_torque_inputs(self) -> 'int':
        '''int: 'NumberOfTorqueInputs' is the original name of this property.'''

        return self.wrapped.NumberOfTorqueInputs

    @number_of_torque_inputs.setter
    def number_of_torque_inputs(self, value: 'int'):
        self.wrapped.NumberOfTorqueInputs = int(value) if value else 0

    @property
    def number_of_speed_inputs(self) -> 'int':
        '''int: 'NumberOfSpeedInputs' is the original name of this property.'''

        return self.wrapped.NumberOfSpeedInputs

    @number_of_speed_inputs.setter
    def number_of_speed_inputs(self, value: 'int'):
        self.wrapped.NumberOfSpeedInputs = int(value) if value else 0

    @property
    def number_of_force_inputs(self) -> 'int':
        '''int: 'NumberOfForceInputs' is the original name of this property.'''

        return self.wrapped.NumberOfForceInputs

    @number_of_force_inputs.setter
    def number_of_force_inputs(self, value: 'int'):
        self.wrapped.NumberOfForceInputs = int(value) if value else 0

    @property
    def number_of_moment_inputs(self) -> 'int':
        '''int: 'NumberOfMomentInputs' is the original name of this property.'''

        return self.wrapped.NumberOfMomentInputs

    @number_of_moment_inputs.setter
    def number_of_moment_inputs(self, value: 'int'):
        self.wrapped.NumberOfMomentInputs = int(value) if value else 0

    @property
    def number_of_boost_pressure_inputs(self) -> 'int':
        '''int: 'NumberOfBoostPressureInputs' is the original name of this property.'''

        return self.wrapped.NumberOfBoostPressureInputs

    @number_of_boost_pressure_inputs.setter
    def number_of_boost_pressure_inputs(self, value: 'int'):
        self.wrapped.NumberOfBoostPressureInputs = int(value) if value else 0

    @property
    def create_load_cases_for_parametric_study_tool(self) -> 'bool':
        '''bool: 'CreateLoadCasesForParametricStudyTool' is the original name of this property.'''

        return self.wrapped.CreateLoadCasesForParametricStudyTool

    @create_load_cases_for_parametric_study_tool.setter
    def create_load_cases_for_parametric_study_tool(self, value: 'bool'):
        self.wrapped.CreateLoadCasesForParametricStudyTool = bool(value) if value else False

    @property
    def design_state_name(self) -> 'str':
        '''str: 'DesignStateName' is the original name of this property.'''

        return self.wrapped.DesignStateName

    @design_state_name.setter
    def design_state_name(self, value: 'str'):
        self.wrapped.DesignStateName = str(value) if value else ''

    @property
    def duty_cycle_duration(self) -> 'float':
        '''float: 'DutyCycleDuration' is the original name of this property.'''

        return self.wrapped.DutyCycleDuration

    @duty_cycle_duration.setter
    def duty_cycle_duration(self, value: 'float'):
        self.wrapped.DutyCycleDuration = float(value) if value else 0.0

    @property
    def torque_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'TorqueChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.TorqueChart.__class__.__mro__:
            raise CastException('Failed to cast torque_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.TorqueChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.TorqueChart.__class__)(self.wrapped.TorqueChart) if self.wrapped.TorqueChart is not None else None

    @property
    def speed_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'SpeedChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.SpeedChart.__class__.__mro__:
            raise CastException('Failed to cast speed_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.SpeedChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SpeedChart.__class__)(self.wrapped.SpeedChart) if self.wrapped.SpeedChart is not None else None

    @property
    def force_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'ForceChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.ForceChart.__class__.__mro__:
            raise CastException('Failed to cast force_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.ForceChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ForceChart.__class__)(self.wrapped.ForceChart) if self.wrapped.ForceChart is not None else None

    @property
    def moment_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'MomentChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.MomentChart.__class__.__mro__:
            raise CastException('Failed to cast moment_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.MomentChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MomentChart.__class__)(self.wrapped.MomentChart) if self.wrapped.MomentChart is not None else None

    @property
    def boost_pressure_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'BoostPressureChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.BoostPressureChart.__class__.__mro__:
            raise CastException('Failed to cast boost_pressure_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.BoostPressureChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.BoostPressureChart.__class__)(self.wrapped.BoostPressureChart) if self.wrapped.BoostPressureChart is not None else None

    @property
    def destination_design_state_column(self) -> 'enum_with_selected_value.EnumWithSelectedValue_DestinationDesignState':
        '''enum_with_selected_value.EnumWithSelectedValue_DestinationDesignState: 'DestinationDesignStateColumn' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_DestinationDesignState.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DestinationDesignStateColumn, value) if self.wrapped.DestinationDesignStateColumn is not None else None

    @destination_design_state_column.setter
    def destination_design_state_column(self, value: 'enum_with_selected_value.EnumWithSelectedValue_DestinationDesignState.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_DestinationDesignState.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.DestinationDesignStateColumn = value

    @property
    def gear_ratios(self) -> 'str':
        '''str: 'GearRatios' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearRatios

    @property
    def time_step_input(self) -> '_6721.TimeStepInputOptions':
        '''TimeStepInputOptions: 'TimeStepInput' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6721.TimeStepInputOptions)(self.wrapped.TimeStepInput) if self.wrapped.TimeStepInput is not None else None

    @property
    def gear_ratio_options(self) -> '_6712.GearRatioInputOptions':
        '''GearRatioInputOptions: 'GearRatioOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6712.GearRatioInputOptions)(self.wrapped.GearRatioOptions) if self.wrapped.GearRatioOptions is not None else None

    @property
    def design_state_options(self) -> '_6709.DesignStateOptions':
        '''DesignStateOptions: 'DesignStateOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6709.DesignStateOptions)(self.wrapped.DesignStateOptions) if self.wrapped.DesignStateOptions is not None else None

    @property
    def load_case_name_inputs(self) -> '_6713.LoadCaseNameOptions':
        '''LoadCaseNameOptions: 'LoadCaseNameInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6713.LoadCaseNameOptions)(self.wrapped.LoadCaseNameInputs) if self.wrapped.LoadCaseNameInputs is not None else None

    @property
    def file_inputs(self) -> 'List[_6715.MultiTimeSeriesDataInputFileOptions]':
        '''List[MultiTimeSeriesDataInputFileOptions]: 'FileInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FileInputs, constructor.new(_6715.MultiTimeSeriesDataInputFileOptions))
        return value

    @property
    def torque_inputs(self) -> 'List[_6722.TorqueInputOptions]':
        '''List[TorqueInputOptions]: 'TorqueInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TorqueInputs, constructor.new(_6722.TorqueInputOptions))
        return value

    @property
    def speed_inputs(self) -> 'List[_6719.SpeedInputOptions]':
        '''List[SpeedInputOptions]: 'SpeedInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpeedInputs, constructor.new(_6719.SpeedInputOptions))
        return value

    @property
    def force_inputs(self) -> 'List[_6711.ForceInputOptions]':
        '''List[ForceInputOptions]: 'ForceInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ForceInputs, constructor.new(_6711.ForceInputOptions))
        return value

    @property
    def moment_inputs(self) -> 'List[_6714.MomentInputOptions]':
        '''List[MomentInputOptions]: 'MomentInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MomentInputs, constructor.new(_6714.MomentInputOptions))
        return value

    @property
    def boost_pressure_inputs(self) -> 'List[_6708.BoostPressureLoadCaseInputOptions]':
        '''List[BoostPressureLoadCaseInputOptions]: 'BoostPressureInputs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.BoostPressureInputs, constructor.new(_6708.BoostPressureLoadCaseInputOptions))
        return value

    @property
    def columns(self) -> 'List[_1586.ColumnTitle]':
        '''List[ColumnTitle]: 'Columns' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Columns, constructor.new(_1586.ColumnTitle))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def create_load_cases(self):
        ''' 'CreateLoadCases' is the original name of this method.'''

        self.wrapped.CreateLoadCases()

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
