'''_1893.py

BearingProtectionDetailsModifier
'''


from typing import List

from mastapy.bearings.bearing_designs.rolling import _1894
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_BEARING_PROTECTION_DETAILS_MODIFIER = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'BearingProtectionDetailsModifier')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingProtectionDetailsModifier',)


class BearingProtectionDetailsModifier(_0.APIBase):
    '''BearingProtectionDetailsModifier

    This is a mastapy class.
    '''

    TYPE = _BEARING_PROTECTION_DETAILS_MODIFIER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingProtectionDetailsModifier.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def current_protection_level(self) -> '_1894.BearingProtectionLevel':
        '''BearingProtectionLevel: 'CurrentProtectionLevel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.CurrentProtectionLevel)
        return constructor.new(_1894.BearingProtectionLevel)(value) if value is not None else None

    @property
    def new_protection_level(self) -> '_1894.BearingProtectionLevel':
        '''BearingProtectionLevel: 'NewProtectionLevel' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.NewProtectionLevel)
        return constructor.new(_1894.BearingProtectionLevel)(value) if value is not None else None

    @new_protection_level.setter
    def new_protection_level(self, value: '_1894.BearingProtectionLevel'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.NewProtectionLevel = value

    @property
    def current_password(self) -> 'str':
        '''str: 'CurrentPassword' is the original name of this property.'''

        return self.wrapped.CurrentPassword

    @current_password.setter
    def current_password(self, value: 'str'):
        self.wrapped.CurrentPassword = str(value) if value else ''

    @property
    def new_password(self) -> 'str':
        '''str: 'NewPassword' is the original name of this property.'''

        return self.wrapped.NewPassword

    @new_password.setter
    def new_password(self, value: 'str'):
        self.wrapped.NewPassword = str(value) if value else ''

    @property
    def confirm_new_password(self) -> 'str':
        '''str: 'ConfirmNewPassword' is the original name of this property.'''

        return self.wrapped.ConfirmNewPassword

    @confirm_new_password.setter
    def confirm_new_password(self, value: 'str'):
        self.wrapped.ConfirmNewPassword = str(value) if value else ''

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
