'''_5384.py

AbstractLoadCaseGroup
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model import _1947
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4120
from mastapy.system_model.analyses_and_results.static_loads import _6666, _6518
from mastapy import _7275, _0
from mastapy._internal.python_net import python_net_import

_ABSTRACT_LOAD_CASE_GROUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups', 'AbstractLoadCaseGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractLoadCaseGroup',)


class AbstractLoadCaseGroup(_0.APIBase):
    '''AbstractLoadCaseGroup

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_LOAD_CASE_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractLoadCaseGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''

    @property
    def total_duration(self) -> 'float':
        '''float: 'TotalDuration' is the original name of this property.'''

        return self.wrapped.TotalDuration

    @total_duration.setter
    def total_duration(self, value: 'float'):
        self.wrapped.TotalDuration = float(value) if value else 0.0

    @property
    def model(self) -> '_1947.Design':
        '''Design: 'Model' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1947.Design)(self.wrapped.Model) if self.wrapped.Model is not None else None

    @property
    def parametric_analysis_options(self) -> '_4120.ParametricStudyToolOptions':
        '''ParametricStudyToolOptions: 'ParametricAnalysisOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_4120.ParametricStudyToolOptions)(self.wrapped.ParametricAnalysisOptions) if self.wrapped.ParametricAnalysisOptions is not None else None

    @property
    def load_case_root_assemblies(self) -> 'List[_6666.RootAssemblyLoadCase]':
        '''List[RootAssemblyLoadCase]: 'LoadCaseRootAssemblies' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCaseRootAssemblies, constructor.new(_6666.RootAssemblyLoadCase))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def create_load_cases(self, number_of_load_cases: 'int', token: '_7275.TaskProgress') -> 'List[_6518.LoadCase]':
        ''' 'CreateLoadCases' is the original name of this method.

        Args:
            number_of_load_cases (int)
            token (mastapy.TaskProgress)

        Returns:
            List[mastapy.system_model.analyses_and_results.static_loads.LoadCase]
        '''

        number_of_load_cases = int(number_of_load_cases)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.CreateLoadCases(number_of_load_cases if number_of_load_cases else 0, token.wrapped if token else None), constructor.new(_6518.LoadCase))

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
