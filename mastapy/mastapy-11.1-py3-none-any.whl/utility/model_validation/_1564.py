'''_1564.py

Status
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.utility.model_validation import _1565
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_STATUS = python_net_import('SMT.MastaAPI.Utility.ModelValidation', 'Status')


__docformat__ = 'restructuredtext en'
__all__ = ('Status',)


class Status(_0.APIBase):
    '''Status

    This is a mastapy class.
    '''

    TYPE = _STATUS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Status.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def has_errors(self) -> 'bool':
        '''bool: 'HasErrors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasErrors

    @property
    def error_count(self) -> 'int':
        '''int: 'ErrorCount' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ErrorCount

    @property
    def has_warnings(self) -> 'bool':
        '''bool: 'HasWarnings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasWarnings

    @property
    def warning_count(self) -> 'int':
        '''int: 'WarningCount' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WarningCount

    @property
    def has_information(self) -> 'bool':
        '''bool: 'HasInformation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasInformation

    @property
    def information_count(self) -> 'int':
        '''int: 'InformationCount' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InformationCount

    @property
    def has_errors_or_warnings(self) -> 'bool':
        '''bool: 'HasErrorsOrWarnings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasErrorsOrWarnings

    @property
    def errors(self) -> 'List[_1565.StatusItem]':
        '''List[StatusItem]: 'Errors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Errors, constructor.new(_1565.StatusItem))
        return value

    @property
    def warnings(self) -> 'List[_1565.StatusItem]':
        '''List[StatusItem]: 'Warnings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Warnings, constructor.new(_1565.StatusItem))
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
