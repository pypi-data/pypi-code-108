"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Any, Union, Literal, Hashable, Optional
from pathlib import Path
from datetime import timezone

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.general_helper.date_time import DateTimeFrame
    from gidapptools.gid_config.parser.config_data import ConfigData
    from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidAppToolsBaseError(Exception):
    """
    Base Exception For GidAppTools.
    """


class DispatchError(GidAppToolsBaseError):
    ...

# TODO: accept AdvancedDict instance as parameter and show path_taken maybe.


class DictMergeConflict(GidAppToolsBaseError):
    def __init__(self, first_dict: dict, second_dict: dict, conflicting_key: Hashable, none_values: set[Hashable]) -> None:
        self.first_dict = first_dict
        self.second_dict = second_dict
        self.conflicting_key = conflicting_key
        self.none_values = none_values
        self.message = f"Unable to merge key {self.conflicting_key!r}, because it already exists in the first dictionary and has an value that is not a 'none_value'({', '.join(f'{item!r}' for item in self.none_values)}"
        super().__init__(self.message)


class AdvancedDictError(GidAppToolsBaseError):
    ...


class GidConfigError(GidAppToolsBaseError):
    ...


class SectionExistsError(GidConfigError):
    ...


class SectionMissingError(GidConfigError):

    def __init__(self, section_name: str, config_data: "ConfigData") -> None:
        self.section_name = section_name
        self.config_data = config_data
        self.message = f"No Section named {self.section_name!r} in config_data {self.config_data}."
        super().__init__(self.message)


class EntryMissingError(GidConfigError):
    def __init__(self, section_name: str, entry_key: str, config_data: "ConfigData") -> None:
        self.section_name = section_name
        self.entry_key = entry_key
        self.config_data = config_data
        self.message = f"No Entry with key {self.entry_key!r} in Section named {self.section_name!r} in config_data {self.config_data}."
        super().__init__(self.message)


class ValueValidationError(GidConfigError):

    def __init__(self, config_value: Any, base_typus: "EntryTypus", validation_description: str = None) -> None:
        self.config_value = config_value
        self.base_typus = base_typus
        self.validation_description = validation_description
        self.msg = f"Value {self.config_value!r} with Base-Typus {self.base_typus!r} failed its validation, {self.validation_description}."
        super().__init__(self.msg)


class ConfigSpecError(GidConfigError):
    ...


class UnconvertableTypusError(ConfigSpecError):
    ...


class ConversionError(GidConfigError):
    ...


class MissingTypusOrSpecError(GidConfigError):
    ...


class IniParsingError(GidConfigError):
    ...


class TrailingCommentError(IniParsingError):
    ...


class EmptyConfigTextError(IniParsingError):
    ...


class KeyPathError(AdvancedDictError):
    def __init__(self, missing_key: Hashable, key_path: list[Hashable], last_key: Hashable = None) -> None:
        self.missing_key = missing_key
        self.last_key = last_key
        self.key_path = key_path if self.last_key is None else key_path + [last_key]
        self.missing_key_pos = self.key_path.index(self.missing_key) + 1
        self.missing_key_pos_verbose = f"{self.missing_key_pos}."
        self.message = f"The {self.missing_key_pos_verbose} key {self.missing_key!r} was not found, full key_path: {self.key_path!r}."
        super().__init__(self.message)


class NotMappingError(AdvancedDictError):
    def __init__(self, key: Hashable, value: Any, key_path: list[Hashable], action: Union[Literal['set'], Literal['get']], last_key: Hashable = None) -> None:
        self.key = key
        self.value = value
        self.value_type = type(value)
        self.action = action
        self.last_key = last_key
        self.key_path = key_path if self.last_key is None else key_path + [last_key]
        self.key_pos = self.key_path.index(self.key) + 1
        self.key_pos_verbose = f"{self.key_pos}."
        self.message = f"Unable to {self.action} {self.key_pos_verbose} {self.key!r} (key_path={self.key_path!r}), because value is not a Mapping but {self.value_type!r}."
        super().__init__(self.message)


class DateTimeFrameTimezoneError(GidAppToolsBaseError):
    def __init__(self, duration_item: "DateTimeFrame", start_tz: Optional[timezone], end_tz: Optional[timezone], message: str) -> None:
        self.duration_item = duration_item
        self.start_tz = start_tz
        self.end_tz = end_tz
        self.message = message + f", {start_tz=}, {end_tz=}."
        super().__init__(self.message)


class BaseMetaDataError(GidAppToolsBaseError):
    """
    Base Error for Meta Data Errors.
    """


class RegisterAfterSetupError(BaseMetaDataError):
    ...


class MetaItemNotFoundError(BaseMetaDataError):
    def __init__(self, requested_name: str, existing_item_names: list[str]) -> None:
        self.requested_name = requested_name
        self.existing_item_names = existing_item_names
        self.message = f"Item {self.requested_name!r} was not found in existing meta_items, existing_meta_item names: {self.existing_item_names!r}"
        super().__init__(self.message)


class NoFactoryFoundError(BaseMetaDataError):
    def __init__(self, app_meta_item_name) -> None:
        self.app_meta_item_name = app_meta_item_name
        self.message = f"Unable to find a factory for {self.app_meta_item_name!r}."
        super().__init__(self.message)


class NotSetupError(BaseMetaDataError):
    def __init__(self, app_meta_data) -> None:
        self.app_meta_data = app_meta_data
        self.message = f'{self.app_meta_data.__class__.__name__!r} has to set up from the base_init_file first!'
        super().__init__(self.message)


class NotBaseInitFileError(BaseMetaDataError):
    """
    Raised if the calling file is not the base __init__.py file of the App.
    """

    def __init__(self, calling_file: Path) -> None:
        self.calling_file = calling_file
        self.calling_folder = calling_file.parent
        self.message = f"This function has to be called from the '__init__.py' file in the base directory of the App, actual calling file: {self.calling_file.as_posix()!r}"
        super().__init__(self.message)


class BaseMetaPathsError(GidAppToolsBaseError):
    """
    Base error for meta_paths.
    """


class AppNameMissingError(BaseMetaPathsError):

    def __init__(self) -> None:
        self.message = "The name of the App was not found in the 'kwargs_holder' or in the env ('APP_NAME')."
        super().__init__(self.message)


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
