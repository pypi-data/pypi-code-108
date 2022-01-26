"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any, Union, Callable, Iterable, Optional
from pathlib import Path
from functools import partial
from threading import RLock
from pprint import pprint

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import EntryMissingError, SectionMissingError, ValueValidationError, MissingTypusOrSpecError
from gidapptools.gid_config.enums import SpecialTypus
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.gid_config.parser.tokens import Section
from gidapptools.gid_config.parser.ini_parser import BaseIniParser
from gidapptools.gid_config.parser.config_data import ConfigFile
from gidapptools.gid_config.conversion.spec_data import SpecFile, SpecVisitor, SpecAttribute
from gidapptools.gid_config.conversion.conversion_table import ConfigValueConversionTable
from gidapptools.gid_config.conversion.entry_typus_item import EntryTypus

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SectionAccessor:

    def __init__(self, config: "GidIniConfig", section_name: str) -> None:
        self.config = config
        self.section_name = section_name

    def get(self,
            entry_key: str,
            typus: Union[type, EntryTypus] = SpecialTypus.AUTO,
            fallback_entry: Iterable[str] = None,
            default: Any = MiscEnum.NOTHING) -> Any:
        return self.config.get(section_name=self.section_name, entry_key=entry_key, typus=typus, fallback_entry=fallback_entry, default=default)

    def set(self,
            entry_key: str,
            entry_value: Any,
            create_missing_section: bool = False,
            spec_typus: str = None) -> None:
        return self.config.set(section_name=self.section_name, entry_key=entry_key, entry_value=entry_value, create_missing_section=create_missing_section, spec_typus=spec_typus)


class GidIniConfig:
    access_locks_storage: dict[tuple, RLock] = {}
    default_spec_visitor: type[SpecVisitor] = SpecVisitor
    default_parser: type[BaseIniParser] = BaseIniParser
    default_converter: type[ConfigValueConversionTable] = ConfigValueConversionTable

    def __init__(self,
                 config_file: Path,
                 config_file_auto_write: bool = True,
                 spec_file: Optional[SpecFile] = None,
                 converter: ConfigValueConversionTable = None,
                 empty_is_missing: bool = True,
                 spec_visitor: SpecVisitor = None,
                 parser: BaseIniParser = None,
                 file_changed_parameter: str = 'size') -> None:

        self.parser = self.default_parser() if parser is None else parser
        self.spec_visitor = self.default_spec_visitor() if spec_visitor is None else spec_visitor
        self.config = ConfigFile(file_path=config_file, parser=self.parser, changed_parameter=file_changed_parameter, auto_write=config_file_auto_write)
        self.spec = SpecFile(file_path=spec_file, visitor=self.spec_visitor, changed_parameter=file_changed_parameter) if spec_file is not None else None
        self.converter = self.default_converter() if converter is None else converter
        self.empty_is_missing = empty_is_missing

    @property
    def access_lock(self) -> RLock:
        spec_path = self.spec.file_path if self.spec is not None else None
        key = (self.config.file_path, spec_path)
        if key not in self.access_locks_storage:
            lock = RLock()
            self.access_locks_storage[key] = lock
        else:
            lock = self.access_locks_storage[key]
        return lock

    def get_description(self, section_name: str, entry_key: str) -> str:
        return self.spec.get(key_path=[section_name, entry_key, SpecAttribute.DESCRIPTION.value], default="")

    def get_gui_visible(self, section_name: str, entry_key: str) -> bool:
        return self.spec.get_gui_visible(section_name=section_name, entry_key=entry_key)

    def get_implemented(self, section_name: str, entry_key: str) -> bool:
        self.get_spec_attribute(section_name=section_name, entry_key=entry_key, attribute=SpecAttribute.IMPLEMENTED, default=True)

    def get_spec_attribute(self, section_name: str, entry_key: str, attribute: Union[SpecAttribute, str], default=None) -> Any:
        return self.spec.get_spec_attribute(section_name=section_name, entry_key=entry_key, attribute=attribute, default=default)

    def reload(self) -> None:
        with self.access_lock:
            self.config.reload()
            self.spec.reload()

    def get_section(self, section_name: str) -> dict[str, Any]:
        with self.access_lock:
            section = self.config.get_section(section_name=section_name)
            return {entry.key: self.get(section_name=section_name, entry_key=entry.key) for entry in section.entries.values()}

    def get_section_accessor(self, section_name: str) -> Callable[[str, Optional[Union[type, EntryTypus]], Optional[Iterable[str]], Optional[Any]], Any]:
        with self.access_lock:
            return partial(self.get, section_name=section_name)

    def get_entry_accessor(self, section_name: str,
                           entry_key: str,
                           typus: Union[type, EntryTypus] = SpecialTypus.AUTO,
                           fallback_entry: Iterable[str] = None,
                           default: Any = MiscEnum.NOTHING):
        return partial(self.get, section_name=section_name, entry_key=entry_key, typus=typus, fallback_entry=fallback_entry, default=default)

    def get(self,
            section_name: str,
            entry_key: str,
            typus: Union[type, EntryTypus] = SpecialTypus.AUTO,
            fallback_entry: Iterable[str] = None,
            default: Any = MiscEnum.NOTHING) -> Any:
        with self.access_lock:
            try:
                entry = self.config.get_entry(section_name=section_name, entry_key=entry_key)

            except (EntryMissingError, SectionMissingError):
                if fallback_entry is not None:
                    return self.get(fallback_entry[0], fallback_entry[1], default=default)
                if default is not MiscEnum.NOTHING:
                    return default
                raise

            if not entry.value:
                if self.empty_is_missing is True:
                    if fallback_entry is not None:
                        return self.get(fallback_entry[0], fallback_entry[1], default=default)
                    if default is not MiscEnum.NOTHING:
                        return default
                spec_default = self.spec._get_entry_default(section_name=section_name, entry_key=entry_key)
                if spec_default not in {MiscEnum.NOTHING, None}:
                    entry.value = spec_default
                else:
                    return None

            if typus is SpecialTypus.AUTO:
                if self.spec is None:
                    raise MissingTypusOrSpecError("You have to provide a typus if no spec file has been set in the __init__.")
                typus = self.spec.get_entry_typus(section_name=section_name, entry_key=entry_key)
            try:
                return self.converter(entry=entry, typus=typus)
            except ValueValidationError:
                if default is not MiscEnum.NOTHING:
                    return default
                raise

    def set(self,
            section_name: str,
            entry_key: str,
            entry_value: Any,
            create_missing_section: bool = False,
            spec_typus: str = None) -> None:
        with self.access_lock:
            self.config.disable_read_event.set()
            try:
                entry_typus = self.spec.get_entry_typus(section_name=section_name, entry_key=entry_key)
                self.config.set_value(section_name=section_name, entry_key=entry_key, entry_value=self.converter.encode(entry_value, entry_typus=entry_typus), create_missing_section=create_missing_section)
                if spec_typus is not None:
                    self.spec.set_typus_value(section_name=section_name, entry_key=entry_key, typus_value=spec_typus)
            finally:
                self.config.disable_read_event.clear()

    def clear_section(self, section_name: str, missing_ok: bool = True) -> None:
        with self.access_lock:
            self.config.clear_entries(section_name=section_name, missing_ok=missing_ok)

    def remove_section(self, section_name: str, missing_ok: bool = True) -> None:
        with self.access_lock:
            self.config.remove_section(section_name=section_name, missing_ok=missing_ok)

    def add_section(self, section_name: str, existing_ok: bool = True) -> None:
        with self.access_lock:
            self.config.add_section(section=Section(section_name), existing_ok=existing_ok)

    def add_spec_value_handler(self, target_name: str, handler: Callable[[Any, list[Any]], EntryTypus]) -> None:
        with self.access_lock:
            self.spec_visitor.add_handler(target_name=target_name, handler=handler)

    def add_converter_function(self, typus: Any, converter_function: Callable) -> None:
        with self.access_lock:
            self.converter[typus] = converter_function

    def as_dict(self, raw: bool = False, with_typus: bool = False, only_gui_visible: bool = False) -> dict[str, dict[str, Any]]:
        with self.access_lock:
            raw_dict = self.config.as_raw_dict()
            if raw is True:
                return raw_dict
            _out = {}
            for section_name, values in raw_dict.items():
                _out[section_name] = {}
                for entry_name in values:
                    if only_gui_visible is True and self.get_gui_visible(section_name, entry_name) is False:
                        continue
                    if with_typus is True:
                        _out[section_name][entry_name] = (self.get(section_name, entry_name), self.get_entry_typus(section_name, entry_name))
                    else:
                        _out[section_name][entry_name] = self.get(section_name, entry_name)

            return _out

    def get_entry_typus(self, section_name: str, entry_key: str):
        return self.spec.get_entry_typus(section_name=section_name, entry_key=entry_key)


# region[Main_Exec]
if __name__ == '__main__':
    pass
    # x = GidIniConfig(config_file=Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\example_config_1.ini"),
    #                  spec_file=Path(r"D:\Dropbox\hobby\Modding\Programs\Github\My_Repos\GidAppTools\tests\gid_config_tests\example_spec_1.json"))
    # x.reload()
# endregion[Main_Exec]
