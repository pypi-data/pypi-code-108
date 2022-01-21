'''_1515.py

UserSpecifiedData
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_USER_SPECIFIED_DATA = python_net_import('SMT.MastaAPI.Utility.Scripting', 'UserSpecifiedData')


__docformat__ = 'restructuredtext en'
__all__ = ('UserSpecifiedData',)


class UserSpecifiedData(_0.APIBase):
    '''UserSpecifiedData

    This is a mastapy class.
    '''

    TYPE = _USER_SPECIFIED_DATA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UserSpecifiedData.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def has_double(self, key: 'str') -> 'bool':
        ''' 'HasDouble' is the original name of this method.

        Args:
            key (str)

        Returns:
            bool
        '''

        key = str(key)
        method_result = self.wrapped.HasDouble(key if key else '')
        return method_result

    def get_double(self, key: 'str') -> 'float':
        ''' 'GetDouble' is the original name of this method.

        Args:
            key (str)

        Returns:
            float
        '''

        key = str(key)
        method_result = self.wrapped.GetDouble(key if key else '')
        return method_result

    def set_double(self, key: 'str', value: 'float'):
        ''' 'SetDouble' is the original name of this method.

        Args:
            key (str)
            value (float)
        '''

        key = str(key)
        value = float(value)
        self.wrapped.SetDouble(key if key else '', value if value else 0.0)

    def has_string(self, key: 'str') -> 'bool':
        ''' 'HasString' is the original name of this method.

        Args:
            key (str)

        Returns:
            bool
        '''

        key = str(key)
        method_result = self.wrapped.HasString(key if key else '')
        return method_result

    def get_string(self, key: 'str') -> 'str':
        ''' 'GetString' is the original name of this method.

        Args:
            key (str)

        Returns:
            str
        '''

        key = str(key)
        method_result = self.wrapped.GetString(key if key else '')
        return method_result

    def set_string(self, key: 'str', value: 'str'):
        ''' 'SetString' is the original name of this method.

        Args:
            key (str)
            value (str)
        '''

        key = str(key)
        value = str(value)
        self.wrapped.SetString(key if key else '', value if value else '')

    def has_bool(self, key: 'str') -> 'bool':
        ''' 'HasBool' is the original name of this method.

        Args:
            key (str)

        Returns:
            bool
        '''

        key = str(key)
        method_result = self.wrapped.HasBool(key if key else '')
        return method_result

    def get_bool(self, key: 'str') -> 'bool':
        ''' 'GetBool' is the original name of this method.

        Args:
            key (str)

        Returns:
            bool
        '''

        key = str(key)
        method_result = self.wrapped.GetBool(key if key else '')
        return method_result

    def set_bool(self, key: 'str', value: 'bool'):
        ''' 'SetBool' is the original name of this method.

        Args:
            key (str)
            value (bool)
        '''

        key = str(key)
        value = bool(value)
        self.wrapped.SetBool(key if key else '', value if value else False)

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
