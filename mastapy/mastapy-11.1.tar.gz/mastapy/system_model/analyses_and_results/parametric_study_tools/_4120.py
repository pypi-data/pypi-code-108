'''_4120.py

ParametricStudyToolOptions
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import overridable, list_with_selected_item, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.analyses_and_results.static_loads import _6532, _6645
from mastapy.system_model import _1955, _1951
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4122, _4123
from mastapy.system_model.analyses_and_results import _2388
from mastapy.math_utility.convergence import _1372
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_TOOL_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyToolOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyToolOptions',)


class ParametricStudyToolOptions(_0.APIBase):
    '''ParametricStudyToolOptions

    This is a mastapy class.
    '''

    TYPE = _PARAMETRIC_STUDY_TOOL_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParametricStudyToolOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_logging_data(self) -> 'bool':
        '''bool: 'IsLoggingData' is the original name of this property.'''

        return self.wrapped.IsLoggingData

    @is_logging_data.setter
    def is_logging_data(self, value: 'bool'):
        self.wrapped.IsLoggingData = bool(value) if value else False

    @property
    def log_report(self) -> 'bool':
        '''bool: 'LogReport' is the original name of this property.'''

        return self.wrapped.LogReport

    @log_report.setter
    def log_report(self, value: 'bool'):
        self.wrapped.LogReport = bool(value) if value else False

    @property
    def changing_design(self) -> 'bool':
        '''bool: 'ChangingDesign' is the original name of this property.'''

        return self.wrapped.ChangingDesign

    @changing_design.setter
    def changing_design(self, value: 'bool'):
        self.wrapped.ChangingDesign = bool(value) if value else False

    @property
    def save_design_at_each_step(self) -> 'bool':
        '''bool: 'SaveDesignAtEachStep' is the original name of this property.'''

        return self.wrapped.SaveDesignAtEachStep

    @save_design_at_each_step.setter
    def save_design_at_each_step(self, value: 'bool'):
        self.wrapped.SaveDesignAtEachStep = bool(value) if value else False

    @property
    def folder_path_for_saved_files(self) -> 'str':
        '''str: 'FolderPathForSavedFiles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FolderPathForSavedFiles

    @property
    def use_multiple_designs(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'UseMultipleDesigns' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.UseMultipleDesigns) if self.wrapped.UseMultipleDesigns is not None else None

    @use_multiple_designs.setter
    def use_multiple_designs(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.UseMultipleDesigns = value

    @property
    def maximum_number_of_design_copies_to_use(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'MaximumNumberOfDesignCopiesToUse' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.MaximumNumberOfDesignCopiesToUse) if self.wrapped.MaximumNumberOfDesignCopiesToUse is not None else None

    @maximum_number_of_design_copies_to_use.setter
    def maximum_number_of_design_copies_to_use(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.MaximumNumberOfDesignCopiesToUse = value

    @property
    def put_newly_added_numerical_variables_into(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'PutNewlyAddedNumericalVariablesInto' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.PutNewlyAddedNumericalVariablesInto) if self.wrapped.PutNewlyAddedNumericalVariablesInto is not None else None

    @put_newly_added_numerical_variables_into.setter
    def put_newly_added_numerical_variables_into(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.PutNewlyAddedNumericalVariablesInto = value

    @property
    def analysis_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_AnalysisType':
        '''enum_with_selected_value.EnumWithSelectedValue_AnalysisType: 'AnalysisType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_AnalysisType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.AnalysisType, value) if self.wrapped.AnalysisType is not None else None

    @analysis_type.setter
    def analysis_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_AnalysisType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_AnalysisType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.AnalysisType = value

    @property
    def number_of_steps(self) -> 'int':
        '''int: 'NumberOfSteps' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfSteps

    @property
    def perform_system_optimisation_pst_post_analysis(self) -> 'bool':
        '''bool: 'PerformSystemOptimisationPSTPostAnalysis' is the original name of this property.'''

        return self.wrapped.PerformSystemOptimisationPSTPostAnalysis

    @perform_system_optimisation_pst_post_analysis.setter
    def perform_system_optimisation_pst_post_analysis(self, value: 'bool'):
        self.wrapped.PerformSystemOptimisationPSTPostAnalysis = bool(value) if value else False

    @property
    def steps_for_statistical_study(self) -> 'int':
        '''int: 'StepsForStatisticalStudy' is the original name of this property.'''

        return self.wrapped.StepsForStatisticalStudy

    @steps_for_statistical_study.setter
    def steps_for_statistical_study(self, value: 'int'):
        self.wrapped.StepsForStatisticalStudy = int(value) if value else 0

    @property
    def steps_in_dimension_1(self) -> 'int':
        '''int: 'StepsInDimension1' is the original name of this property.'''

        return self.wrapped.StepsInDimension1

    @steps_in_dimension_1.setter
    def steps_in_dimension_1(self, value: 'int'):
        self.wrapped.StepsInDimension1 = int(value) if value else 0

    @property
    def parametric_study_type(self) -> '_6645.ParametricStudyType':
        '''ParametricStudyType: 'ParametricStudyType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ParametricStudyType)
        return constructor.new(_6645.ParametricStudyType)(value) if value is not None else None

    @parametric_study_type.setter
    def parametric_study_type(self, value: '_6645.ParametricStudyType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ParametricStudyType = value

    @property
    def steps_in_dimension_2(self) -> 'int':
        '''int: 'StepsInDimension2' is the original name of this property.'''

        return self.wrapped.StepsInDimension2

    @steps_in_dimension_2.setter
    def steps_in_dimension_2(self, value: 'int'):
        self.wrapped.StepsInDimension2 = int(value) if value else 0

    @property
    def number_of_analysis_dimensions(self) -> 'int':
        '''int: 'NumberOfAnalysisDimensions' is the original name of this property.'''

        return self.wrapped.NumberOfAnalysisDimensions

    @number_of_analysis_dimensions.setter
    def number_of_analysis_dimensions(self, value: 'int'):
        self.wrapped.NumberOfAnalysisDimensions = int(value) if value else 0

    @property
    def external_full_fe_loader(self) -> '_1955.ExternalFullFELoader':
        '''ExternalFullFELoader: 'ExternalFullFELoader' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1955.ExternalFullFELoader)(self.wrapped.ExternalFullFELoader) if self.wrapped.ExternalFullFELoader is not None else None

    @property
    def step_results(self) -> 'List[_4122.ParametricStudyToolStepResult]':
        '''List[ParametricStudyToolStepResult]: 'StepResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StepResults, constructor.new(_4122.ParametricStudyToolStepResult))
        return value

    @property
    def study_variables(self) -> 'List[_4123.ParametricStudyVariable]':
        '''List[ParametricStudyVariable]: 'StudyVariables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.StudyVariables, constructor.new(_4123.ParametricStudyVariable))
        return value

    @property
    def parametric_study_logging_variables(self) -> 'List[_2388.AnalysisCaseVariable]':
        '''List[AnalysisCaseVariable]: 'ParametricStudyLoggingVariables' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ParametricStudyLoggingVariables, constructor.new(_2388.AnalysisCaseVariable))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def edit_folder_path(self):
        ''' 'EditFolderPath' is the original name of this method.'''

        self.wrapped.EditFolderPath()

    def data_logger_for(self, design_entity: '_1951.DesignEntity') -> '_1372.DataLogger':
        ''' 'DataLoggerFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.DesignEntity)

        Returns:
            mastapy.math_utility.convergence.DataLogger
        '''

        method_result = self.wrapped.DataLoggerFor(design_entity.wrapped if design_entity else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def add_study_variable(self, design_entity: '_1951.DesignEntity', path: 'List[str]') -> '_4123.ParametricStudyVariable':
        ''' 'AddStudyVariable' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.DesignEntity)
            path (List[str])

        Returns:
            mastapy.system_model.analyses_and_results.parametric_study_tools.ParametricStudyVariable
        '''

        path = conversion.mp_to_pn_objects_in_list(path)
        method_result = self.wrapped.AddStudyVariable(design_entity.wrapped if design_entity else None, path)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def remove_study_variable(self, study_variable: '_4123.ParametricStudyVariable'):
        ''' 'RemoveStudyVariable' is the original name of this method.

        Args:
            study_variable (mastapy.system_model.analyses_and_results.parametric_study_tools.ParametricStudyVariable)
        '''

        self.wrapped.RemoveStudyVariable(study_variable.wrapped if study_variable else None)

    def move_study_variable_up(self, study_variable: '_4123.ParametricStudyVariable'):
        ''' 'MoveStudyVariableUp' is the original name of this method.

        Args:
            study_variable (mastapy.system_model.analyses_and_results.parametric_study_tools.ParametricStudyVariable)
        '''

        self.wrapped.MoveStudyVariableUp(study_variable.wrapped if study_variable else None)

    def move_study_variable_down(self, study_variable: '_4123.ParametricStudyVariable'):
        ''' 'MoveStudyVariableDown' is the original name of this method.

        Args:
            study_variable (mastapy.system_model.analyses_and_results.parametric_study_tools.ParametricStudyVariable)
        '''

        self.wrapped.MoveStudyVariableDown(study_variable.wrapped if study_variable else None)

    def add_logging_variable(self, design_entity: '_1951.DesignEntity', path: 'List[str]') -> '_2388.AnalysisCaseVariable':
        ''' 'AddLoggingVariable' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.DesignEntity)
            path (List[str])

        Returns:
            mastapy.system_model.analyses_and_results.AnalysisCaseVariable
        '''

        path = conversion.mp_to_pn_objects_in_list(path)
        method_result = self.wrapped.AddLoggingVariable(design_entity.wrapped if design_entity else None, path)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def remove_logging_variable(self, analysis_variable: '_2388.AnalysisCaseVariable'):
        ''' 'RemoveLoggingVariable' is the original name of this method.

        Args:
            analysis_variable (mastapy.system_model.analyses_and_results.AnalysisCaseVariable)
        '''

        self.wrapped.RemoveLoggingVariable(analysis_variable.wrapped if analysis_variable else None)

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
