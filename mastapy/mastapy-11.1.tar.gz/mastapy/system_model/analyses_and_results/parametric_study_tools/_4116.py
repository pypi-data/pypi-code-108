'''_4116.py

ParametricStudyDOEResultVariableForParallelCoordinatesPlot
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_DOE_RESULT_VARIABLE_FOR_PARALLEL_COORDINATES_PLOT = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyDOEResultVariableForParallelCoordinatesPlot')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyDOEResultVariableForParallelCoordinatesPlot',)


class ParametricStudyDOEResultVariableForParallelCoordinatesPlot(_0.APIBase):
    '''ParametricStudyDOEResultVariableForParallelCoordinatesPlot

    This is a mastapy class.
    '''

    TYPE = _PARAMETRIC_STUDY_DOE_RESULT_VARIABLE_FOR_PARALLEL_COORDINATES_PLOT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParametricStudyDOEResultVariableForParallelCoordinatesPlot.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def parameter_name(self) -> 'str':
        '''str: 'ParameterName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParameterName

    @property
    def entity_name(self) -> 'str':
        '''str: 'EntityName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EntityName

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def delete(self):
        ''' 'Delete' is the original name of this method.'''

        self.wrapped.Delete()

    def move_up(self):
        ''' 'MoveUp' is the original name of this method.'''

        self.wrapped.MoveUp()

    def move_down(self):
        ''' 'MoveDown' is the original name of this method.'''

        self.wrapped.MoveDown()

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
