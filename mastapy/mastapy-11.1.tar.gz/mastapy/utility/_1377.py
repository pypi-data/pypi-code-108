'''_1377.py

ExecutableDirectoryCopier
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_EXECUTABLE_DIRECTORY_COPIER = python_net_import('SMT.MastaAPI.Utility', 'ExecutableDirectoryCopier')


__docformat__ = 'restructuredtext en'
__all__ = ('ExecutableDirectoryCopier',)


class ExecutableDirectoryCopier(_0.APIBase):
    '''ExecutableDirectoryCopier

    This is a mastapy class.
    '''

    TYPE = _EXECUTABLE_DIRECTORY_COPIER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExecutableDirectoryCopier.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def message(self) -> 'str':
        '''str: 'Message' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Message

    @property
    def space_required_for_local_copy(self) -> 'str':
        '''str: 'SpaceRequiredForLocalCopy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpaceRequiredForLocalCopy

    @property
    def local_copy_parent_directory(self) -> 'str':
        '''str: 'LocalCopyParentDirectory' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalCopyParentDirectory

    @property
    def local_copy_found_at(self) -> 'str':
        '''str: 'LocalCopyFoundAt' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LocalCopyFoundAt

    @property
    def selected_option(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ExecutableDirectoryCopier_Option':
        '''enum_with_selected_value.EnumWithSelectedValue_ExecutableDirectoryCopier_Option: 'SelectedOption' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ExecutableDirectoryCopier_Option.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.SelectedOption, value) if self.wrapped.SelectedOption is not None else None

    @selected_option.setter
    def selected_option(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ExecutableDirectoryCopier_Option.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ExecutableDirectoryCopier_Option.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.SelectedOption = value

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
