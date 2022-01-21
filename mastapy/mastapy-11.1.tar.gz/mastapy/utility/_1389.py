'''_1389.py

ProgramSettings
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility import _1387
from mastapy._internal.python_net import python_net_import

_PROGRAM_SETTINGS = python_net_import('SMT.MastaAPI.Utility', 'ProgramSettings')


__docformat__ = 'restructuredtext en'
__all__ = ('ProgramSettings',)


class ProgramSettings(_1387.PerMachineSettings):
    '''ProgramSettings

    This is a mastapy class.
    '''

    TYPE = _PROGRAM_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ProgramSettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_number_of_undo_items(self) -> 'int':
        '''int: 'MaximumNumberOfUndoItems' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfUndoItems

    @maximum_number_of_undo_items.setter
    def maximum_number_of_undo_items(self, value: 'int'):
        self.wrapped.MaximumNumberOfUndoItems = int(value) if value else 0

    @property
    def number_of_cpu_threads(self) -> 'int':
        '''int: 'NumberOfCPUThreads' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfCPUThreads

    @property
    def number_of_cpu_cores(self) -> 'int':
        '''int: 'NumberOfCPUCores' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfCPUCores

    @property
    def maximum_number_of_threads_for_large_operations(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'MaximumNumberOfThreadsForLargeOperations' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.MaximumNumberOfThreadsForLargeOperations) if self.wrapped.MaximumNumberOfThreadsForLargeOperations is not None else None

    @maximum_number_of_threads_for_large_operations.setter
    def maximum_number_of_threads_for_large_operations(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.MaximumNumberOfThreadsForLargeOperations = value

    @property
    def maximum_number_of_threads_for_mathematically_intensive_operations(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'MaximumNumberOfThreadsForMathematicallyIntensiveOperations' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.MaximumNumberOfThreadsForMathematicallyIntensiveOperations) if self.wrapped.MaximumNumberOfThreadsForMathematicallyIntensiveOperations is not None else None

    @maximum_number_of_threads_for_mathematically_intensive_operations.setter
    def maximum_number_of_threads_for_mathematically_intensive_operations(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.MaximumNumberOfThreadsForMathematicallyIntensiveOperations = value

    @property
    def allow_multithreading(self) -> 'bool':
        '''bool: 'AllowMultithreading' is the original name of this property.'''

        return self.wrapped.AllowMultithreading

    @allow_multithreading.setter
    def allow_multithreading(self, value: 'bool'):
        self.wrapped.AllowMultithreading = bool(value) if value else False

    @property
    def use_standard_dialog_for_file_save(self) -> 'bool':
        '''bool: 'UseStandardDialogForFileSave' is the original name of this property.'''

        return self.wrapped.UseStandardDialogForFileSave

    @use_standard_dialog_for_file_save.setter
    def use_standard_dialog_for_file_save(self, value: 'bool'):
        self.wrapped.UseStandardDialogForFileSave = bool(value) if value else False

    @property
    def use_standard_dialog_for_file_open(self) -> 'bool':
        '''bool: 'UseStandardDialogForFileOpen' is the original name of this property.'''

        return self.wrapped.UseStandardDialogForFileOpen

    @use_standard_dialog_for_file_open.setter
    def use_standard_dialog_for_file_open(self, value: 'bool'):
        self.wrapped.UseStandardDialogForFileOpen = bool(value) if value else False

    @property
    def include_overridable_property_source_information(self) -> 'bool':
        '''bool: 'IncludeOverridablePropertySourceInformation' is the original name of this property.'''

        return self.wrapped.IncludeOverridablePropertySourceInformation

    @include_overridable_property_source_information.setter
    def include_overridable_property_source_information(self, value: 'bool'):
        self.wrapped.IncludeOverridablePropertySourceInformation = bool(value) if value else False

    @property
    def autosave_interval_minutes(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'AutosaveIntervalMinutes' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.AutosaveIntervalMinutes) if self.wrapped.AutosaveIntervalMinutes is not None else None

    @autosave_interval_minutes.setter
    def autosave_interval_minutes(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.AutosaveIntervalMinutes = value

    @property
    def use_default_autosave_directory(self) -> 'bool':
        '''bool: 'UseDefaultAutosaveDirectory' is the original name of this property.'''

        return self.wrapped.UseDefaultAutosaveDirectory

    @use_default_autosave_directory.setter
    def use_default_autosave_directory(self, value: 'bool'):
        self.wrapped.UseDefaultAutosaveDirectory = bool(value) if value else False

    @property
    def user_defined_autosave_directory(self) -> 'str':
        '''str: 'UserDefinedAutosaveDirectory' is the original name of this property.'''

        return self.wrapped.UserDefinedAutosaveDirectory

    @user_defined_autosave_directory.setter
    def user_defined_autosave_directory(self, value: 'str'):
        self.wrapped.UserDefinedAutosaveDirectory = str(value) if value else ''

    @property
    def autosave_directory(self) -> 'str':
        '''str: 'AutosaveDirectory' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AutosaveDirectory

    @property
    def use_background_saving(self) -> 'bool':
        '''bool: 'UseBackgroundSaving' is the original name of this property.'''

        return self.wrapped.UseBackgroundSaving

    @use_background_saving.setter
    def use_background_saving(self, value: 'bool'):
        self.wrapped.UseBackgroundSaving = bool(value) if value else False

    @property
    def auto_return_licences_inactivity_interval_minutes(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'AutoReturnLicencesInactivityIntervalMinutes' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.AutoReturnLicencesInactivityIntervalMinutes) if self.wrapped.AutoReturnLicencesInactivityIntervalMinutes is not None else None

    @auto_return_licences_inactivity_interval_minutes.setter
    def auto_return_licences_inactivity_interval_minutes(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.AutoReturnLicencesInactivityIntervalMinutes = value

    @property
    def maximum_number_of_files_to_store_in_history(self) -> 'int':
        '''int: 'MaximumNumberOfFilesToStoreInHistory' is the original name of this property.'''

        return self.wrapped.MaximumNumberOfFilesToStoreInHistory

    @maximum_number_of_files_to_store_in_history.setter
    def maximum_number_of_files_to_store_in_history(self, value: 'int'):
        self.wrapped.MaximumNumberOfFilesToStoreInHistory = int(value) if value else 0

    @property
    def confirm_exit(self) -> 'bool':
        '''bool: 'ConfirmExit' is the original name of this property.'''

        return self.wrapped.ConfirmExit

    @confirm_exit.setter
    def confirm_exit(self, value: 'bool'):
        self.wrapped.ConfirmExit = bool(value) if value else False

    @property
    def use_compression_for_masta_files(self) -> 'bool':
        '''bool: 'UseCompressionForMASTAFiles' is the original name of this property.'''

        return self.wrapped.UseCompressionForMASTAFiles

    @use_compression_for_masta_files.setter
    def use_compression_for_masta_files(self, value: 'bool'):
        self.wrapped.UseCompressionForMASTAFiles = bool(value) if value else False

    @property
    def font_size(self) -> 'float':
        '''float: 'FontSize' is the original name of this property.'''

        return self.wrapped.FontSize

    @font_size.setter
    def font_size(self, value: 'float'):
        self.wrapped.FontSize = float(value) if value else 0.0

    @property
    def override_font(self) -> 'str':
        '''str: 'OverrideFont' is the original name of this property.'''

        return self.wrapped.OverrideFont

    @override_font.setter
    def override_font(self, value: 'str'):
        self.wrapped.OverrideFont = str(value) if value else ''

    @property
    def check_for_new_version_on_startup(self) -> 'bool':
        '''bool: 'CheckForNewVersionOnStartup' is the original name of this property.'''

        return self.wrapped.CheckForNewVersionOnStartup

    @check_for_new_version_on_startup.setter
    def check_for_new_version_on_startup(self, value: 'bool'):
        self.wrapped.CheckForNewVersionOnStartup = bool(value) if value else False

    @property
    def show_number_of_teeth_with_gear_set_names(self) -> 'bool':
        '''bool: 'ShowNumberOfTeethWithGearSetNames' is the original name of this property.'''

        return self.wrapped.ShowNumberOfTeethWithGearSetNames

    @show_number_of_teeth_with_gear_set_names.setter
    def show_number_of_teeth_with_gear_set_names(self, value: 'bool'):
        self.wrapped.ShowNumberOfTeethWithGearSetNames = bool(value) if value else False

    @property
    def show_drawing_numbers_in_tree_view(self) -> 'bool':
        '''bool: 'ShowDrawingNumbersInTreeView' is the original name of this property.'''

        return self.wrapped.ShowDrawingNumbersInTreeView

    @show_drawing_numbers_in_tree_view.setter
    def show_drawing_numbers_in_tree_view(self, value: 'bool'):
        self.wrapped.ShowDrawingNumbersInTreeView = bool(value) if value else False

    @property
    def ask_for_part_names_in_the_2d_view(self) -> 'bool':
        '''bool: 'AskForPartNamesInThe2DView' is the original name of this property.'''

        return self.wrapped.AskForPartNamesInThe2DView

    @ask_for_part_names_in_the_2d_view.setter
    def ask_for_part_names_in_the_2d_view(self, value: 'bool'):
        self.wrapped.AskForPartNamesInThe2DView = bool(value) if value else False

    @property
    def number_of_connections_to_show_when_multi_selecting(self) -> 'int':
        '''int: 'NumberOfConnectionsToShowWhenMultiSelecting' is the original name of this property.'''

        return self.wrapped.NumberOfConnectionsToShowWhenMultiSelecting

    @number_of_connections_to_show_when_multi_selecting.setter
    def number_of_connections_to_show_when_multi_selecting(self, value: 'int'):
        self.wrapped.NumberOfConnectionsToShowWhenMultiSelecting = int(value) if value else 0

    @property
    def show_tutorial_on_startup(self) -> 'bool':
        '''bool: 'ShowTutorialOnStartup' is the original name of this property.'''

        return self.wrapped.ShowTutorialOnStartup

    @show_tutorial_on_startup.setter
    def show_tutorial_on_startup(self, value: 'bool'):
        self.wrapped.ShowTutorialOnStartup = bool(value) if value else False

    @property
    def number_of_days_of_advance_warning_for_expiring_features(self) -> 'int':
        '''int: 'NumberOfDaysOfAdvanceWarningForExpiringFeatures' is the original name of this property.'''

        return self.wrapped.NumberOfDaysOfAdvanceWarningForExpiringFeatures

    @number_of_days_of_advance_warning_for_expiring_features.setter
    def number_of_days_of_advance_warning_for_expiring_features(self, value: 'int'):
        self.wrapped.NumberOfDaysOfAdvanceWarningForExpiringFeatures = int(value) if value else 0

    @property
    def prompt_to_copy_network_executable_directory_locally(self) -> 'bool':
        '''bool: 'PromptToCopyNetworkExecutableDirectoryLocally' is the original name of this property.'''

        return self.wrapped.PromptToCopyNetworkExecutableDirectoryLocally

    @prompt_to_copy_network_executable_directory_locally.setter
    def prompt_to_copy_network_executable_directory_locally(self, value: 'bool'):
        self.wrapped.PromptToCopyNetworkExecutableDirectoryLocally = bool(value) if value else False

    def select_autosave_directory(self):
        ''' 'SelectAutosaveDirectory' is the original name of this method.'''

        self.wrapped.SelectAutosaveDirectory()

    def clear_mru_entries(self):
        ''' 'ClearMRUEntries' is the original name of this method.'''

        self.wrapped.ClearMRUEntries()
