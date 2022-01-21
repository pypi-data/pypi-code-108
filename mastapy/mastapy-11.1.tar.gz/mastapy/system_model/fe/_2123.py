'''_2123.py

FEStiffnessTester
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.fe import _2124
from mastapy.math_utility.measured_vectors import _1359
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_STIFFNESS_TESTER = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FEStiffnessTester')


__docformat__ = 'restructuredtext en'
__all__ = ('FEStiffnessTester',)


class FEStiffnessTester(_0.APIBase):
    '''FEStiffnessTester

    This is a mastapy class.
    '''

    TYPE = _FE_STIFFNESS_TESTER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEStiffnessTester.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def force_scaling_factor(self) -> 'float':
        '''float: 'ForceScalingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ForceScalingFactor

    @property
    def displacement_scaling_factor(self) -> 'float':
        '''float: 'DisplacementScalingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DisplacementScalingFactor

    @property
    def fe_stiffness(self) -> '_2124.FESubstructure':
        '''FESubstructure: 'FEStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2124.FESubstructure)(self.wrapped.FEStiffness) if self.wrapped.FEStiffness is not None else None

    @property
    def force_and_displacement_results(self) -> 'List[_1359.ForceAndDisplacementResults]':
        '''List[ForceAndDisplacementResults]: 'ForceAndDisplacementResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ForceAndDisplacementResults, constructor.new(_1359.ForceAndDisplacementResults))
        return value

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
