'''_2155.py

FESubstructureVersionComparer
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.fe.version_comparer import _2157, _2153
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_SUBSTRUCTURE_VERSION_COMPARER = python_net_import('SMT.MastaAPI.SystemModel.FE.VersionComparer', 'FESubstructureVersionComparer')


__docformat__ = 'restructuredtext en'
__all__ = ('FESubstructureVersionComparer',)


class FESubstructureVersionComparer(_0.APIBase):
    '''FESubstructureVersionComparer

    This is a mastapy class.
    '''

    TYPE = _FE_SUBSTRUCTURE_VERSION_COMPARER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FESubstructureVersionComparer.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def save_new_design_files(self) -> 'bool':
        '''bool: 'SaveNewDesignFiles' is the original name of this property.'''

        return self.wrapped.SaveNewDesignFiles

    @save_new_design_files.setter
    def save_new_design_files(self, value: 'bool'):
        self.wrapped.SaveNewDesignFiles = bool(value) if value else False

    @property
    def check_all_files_in_directory(self) -> 'bool':
        '''bool: 'CheckAllFilesInDirectory' is the original name of this property.'''

        return self.wrapped.CheckAllFilesInDirectory

    @check_all_files_in_directory.setter
    def check_all_files_in_directory(self, value: 'bool'):
        self.wrapped.CheckAllFilesInDirectory = bool(value) if value else False

    @property
    def file(self) -> 'str':
        '''str: 'File' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.File

    @property
    def folder_path_for_saved_files(self) -> 'str':
        '''str: 'FolderPathForSavedFiles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FolderPathForSavedFiles

    @property
    def status(self) -> 'str':
        '''str: 'Status' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Status

    @property
    def load_cases_to_run(self) -> '_2157.LoadCasesToRun':
        '''LoadCasesToRun: 'LoadCasesToRun' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.LoadCasesToRun)
        return constructor.new(_2157.LoadCasesToRun)(value) if value is not None else None

    @load_cases_to_run.setter
    def load_cases_to_run(self, value: '_2157.LoadCasesToRun'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.LoadCasesToRun = value

    @property
    def design_results(self) -> 'List[_2153.DesignResults]':
        '''List[DesignResults]: 'DesignResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.DesignResults, constructor.new(_2153.DesignResults))
        return value

    @property
    def report_names(self) -> 'List[str]':
        '''List[str]: 'ReportNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ReportNames, str)
        return value

    def edit_folder_path(self):
        ''' 'EditFolderPath' is the original name of this method.'''

        self.wrapped.EditFolderPath()

    def select_file(self):
        ''' 'SelectFile' is the original name of this method.'''

        self.wrapped.SelectFile()

    def run(self):
        ''' 'Run' is the original name of this method.'''

        self.wrapped.Run()

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
