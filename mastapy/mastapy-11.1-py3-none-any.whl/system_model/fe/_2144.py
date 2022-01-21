'''_2144.py

OptionsWhenExternalFEFileAlreadyExists
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OPTIONS_WHEN_EXTERNAL_FE_FILE_ALREADY_EXISTS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'OptionsWhenExternalFEFileAlreadyExists')


__docformat__ = 'restructuredtext en'
__all__ = ('OptionsWhenExternalFEFileAlreadyExists',)


class OptionsWhenExternalFEFileAlreadyExists(_0.APIBase):
    '''OptionsWhenExternalFEFileAlreadyExists

    This is a mastapy class.
    '''

    TYPE = _OPTIONS_WHEN_EXTERNAL_FE_FILE_ALREADY_EXISTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OptionsWhenExternalFEFileAlreadyExists.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def overwrite_existing_mesh_file(self) -> 'bool':
        '''bool: 'OverwriteExistingMeshFile' is the original name of this property.'''

        return self.wrapped.OverwriteExistingMeshFile

    @overwrite_existing_mesh_file.setter
    def overwrite_existing_mesh_file(self, value: 'bool'):
        self.wrapped.OverwriteExistingMeshFile = bool(value) if value else False

    @property
    def overwrite_existing_vectors_file(self) -> 'bool':
        '''bool: 'OverwriteExistingVectorsFile' is the original name of this property.'''

        return self.wrapped.OverwriteExistingVectorsFile

    @overwrite_existing_vectors_file.setter
    def overwrite_existing_vectors_file(self, value: 'bool'):
        self.wrapped.OverwriteExistingVectorsFile = bool(value) if value else False

    @property
    def output_mesh_file_path(self) -> 'str':
        '''str: 'OutputMeshFilePath' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OutputMeshFilePath

    @property
    def output_vectors_file_path(self) -> 'str':
        '''str: 'OutputVectorsFilePath' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OutputVectorsFilePath

    @property
    def append_current_date_and_time_to_new_file_names(self) -> 'bool':
        '''bool: 'AppendCurrentDateAndTimeToNewFileNames' is the original name of this property.'''

        return self.wrapped.AppendCurrentDateAndTimeToNewFileNames

    @append_current_date_and_time_to_new_file_names.setter
    def append_current_date_and_time_to_new_file_names(self, value: 'bool'):
        self.wrapped.AppendCurrentDateAndTimeToNewFileNames = bool(value) if value else False

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
