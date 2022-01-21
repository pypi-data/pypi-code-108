'''_2158.py

NodeComparisonResult
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility.measured_vectors import _1361, _1363
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NODE_COMPARISON_RESULT = python_net_import('SMT.MastaAPI.SystemModel.FE.VersionComparer', 'NodeComparisonResult')


__docformat__ = 'restructuredtext en'
__all__ = ('NodeComparisonResult',)


class NodeComparisonResult(_0.APIBase):
    '''NodeComparisonResult

    This is a mastapy class.
    '''

    TYPE = _NODE_COMPARISON_RESULT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodeComparisonResult.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def details(self) -> 'str':
        '''str: 'Details' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Details

    @property
    def linear_change(self) -> 'float':
        '''float: 'LinearChange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LinearChange

    @property
    def angular_change(self) -> 'float':
        '''float: 'AngularChange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularChange

    @property
    def original_result(self) -> '_1361.NodeResults':
        '''NodeResults: 'OriginalResult' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1361.NodeResults)(self.wrapped.OriginalResult) if self.wrapped.OriginalResult is not None else None

    @property
    def new_result(self) -> '_1361.NodeResults':
        '''NodeResults: 'NewResult' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1361.NodeResults)(self.wrapped.NewResult) if self.wrapped.NewResult is not None else None

    @property
    def displacement_change(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'DisplacementChange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.DisplacementChange) if self.wrapped.DisplacementChange is not None else None

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
