'''_1587.py

TextFileDelimiterOptions
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TEXT_FILE_DELIMITER_OPTIONS = python_net_import('SMT.MastaAPI.Utility.FileAccessHelpers', 'TextFileDelimiterOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('TextFileDelimiterOptions',)


class TextFileDelimiterOptions(_0.APIBase):
    '''TextFileDelimiterOptions

    This is a mastapy class.
    '''

    TYPE = _TEXT_FILE_DELIMITER_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TextFileDelimiterOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_comma(self) -> 'bool':
        '''bool: 'UseComma' is the original name of this property.'''

        return self.wrapped.UseComma

    @use_comma.setter
    def use_comma(self, value: 'bool'):
        self.wrapped.UseComma = bool(value) if value else False

    @property
    def use_tab(self) -> 'bool':
        '''bool: 'UseTab' is the original name of this property.'''

        return self.wrapped.UseTab

    @use_tab.setter
    def use_tab(self, value: 'bool'):
        self.wrapped.UseTab = bool(value) if value else False

    @property
    def use_space(self) -> 'bool':
        '''bool: 'UseSpace' is the original name of this property.'''

        return self.wrapped.UseSpace

    @use_space.setter
    def use_space(self, value: 'bool'):
        self.wrapped.UseSpace = bool(value) if value else False

    @property
    def use_semi_colon(self) -> 'bool':
        '''bool: 'UseSemiColon' is the original name of this property.'''

        return self.wrapped.UseSemiColon

    @use_semi_colon.setter
    def use_semi_colon(self, value: 'bool'):
        self.wrapped.UseSemiColon = bool(value) if value else False

    @property
    def other(self) -> 'str':
        '''str: 'Other' is the original name of this property.'''

        return self.wrapped.Other

    @other.setter
    def other(self, value: 'str'):
        self.wrapped.Other = str(value) if value else ''

    @property
    def treat_consecutive_delimiters_as_one(self) -> 'bool':
        '''bool: 'TreatConsecutiveDelimitersAsOne' is the original name of this property.'''

        return self.wrapped.TreatConsecutiveDelimitersAsOne

    @treat_consecutive_delimiters_as_one.setter
    def treat_consecutive_delimiters_as_one(self, value: 'bool'):
        self.wrapped.TreatConsecutiveDelimitersAsOne = bool(value) if value else False

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
