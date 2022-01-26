"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Any, Union, Literal
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import EntryMissingError, SectionExistsError, SectionMissingError
from gidapptools.gid_config.parser.tokens import Entry, Section, EnvSection
from gidapptools.gid_config.parser.ini_parser import BaseIniParser
from gidapptools.general_helper.mixins.file_mixin import FileMixin

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    pass

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConfigData:
    env_section = EnvSection()

    def __init__(self) -> None:
        self._sections: dict[str, Section] = None

    @property
    def sections(self) -> dict[str, Section]:
        if self._sections is None:
            self._sections = {}
        return self._sections

    @property
    def all_sections(self) -> tuple[Section]:
        return tuple(self.sections.values())

    @property
    def all_section_names(self) -> tuple[str]:
        return tuple(self.sections)

    def get_section(self, section_name: str, create_missing_section: bool = False) -> Section:
        try:
            return self.sections[section_name]
        except KeyError as error:
            if create_missing_section is False:
                raise SectionMissingError(section_name=section_name, config_data=self) from error
            section = Section(section_name)
            self.add_section(section=section)
            return section

    def add_section(self, section, existing_ok: bool = True) -> bool:
        if section.name in self._sections:
            if existing_ok is True:
                return False
            raise SectionExistsError(f"Section {section.name!r} already exists.")
        self._sections[section.name] = section
        return True

    def remove_section(self, section_name: str, missing_ok: bool = False) -> bool:
        try:
            del self._sections[section_name]
            return True
        except KeyError as error:
            if missing_ok is False:
                raise SectionMissingError(section_name=section_name, config_data=self) from error
            return False

    def clear_all_sections(self) -> bool:
        self._sections = None
        return True

    def get_entry(self, section_name: str, entry_key: str, create_missing_section: bool = False) -> Entry:
        section = self.get_section(section_name=section_name, create_missing_section=create_missing_section)
        try:
            return section[entry_key]
        except KeyError as error:
            raise EntryMissingError(section_name=section_name, entry_key=entry_key, config_data=self) from error

    def add_entry(self, section_name: str, entry: Entry, create_missing_section: bool = False) -> bool:
        section = self.get_section(section_name=section_name, create_missing_section=create_missing_section)
        section.add_entry(entry=entry)
        return True

    def set_value(self, section_name: str, entry_key: str, entry_value: str, create_missing_section: bool = False) -> bool:
        try:
            entry = self.get_entry(section_name=section_name, entry_key=entry_key, create_missing_section=create_missing_section)
            entry.value = entry_value

        except EntryMissingError:
            entry = Entry(entry_key, entry_value)
            self.add_entry(section_name=section_name, entry=entry, create_missing_section=create_missing_section)
        return True

    def remove_entry(self, section_name: str, entry_key: str, missing_ok: bool = False) -> bool:
        try:
            section = self.get_section(section_name=section_name)
        except SectionMissingError:
            if missing_ok is False:
                raise
            return False

        try:
            del section[entry_key]
            return True
        except KeyError as error:
            if missing_ok is False:
                raise EntryMissingError(section_name=section_name, entry_key=entry_key, config_data=self) from error
            return False

    def clear_entries(self, section_name: str, missing_ok: bool = False) -> bool:
        try:
            section = self.get_section(section_name=section_name)
            section.entries = {}
            return True
        except SectionMissingError:
            if missing_ok is False:
                raise
            return False

    def reload(self) -> None:
        pass

    def as_raw_dict(self) -> dict[str, dict[str, Any]]:
        _out = {}
        sections = self.sections.copy()
        sections.pop(self.env_section.name)
        for section in sections.values():

            _out |= section.as_dict()
        return _out


class ConfigFile(FileMixin, ConfigData):

    def __init__(self,
                 file_path: Path,
                 parser: BaseIniParser,
                 changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size',
                 auto_write: bool = True,
                 **kwargs) -> None:

        self.parser = parser
        self.auto_write = auto_write
        super().__init__(file_path=file_path, changed_parameter=changed_parameter, **kwargs)

    def _do_auto_write(self, success: bool) -> None:
        if success is True and self.auto_write is True:
            self.save()

    @property
    def sections(self) -> dict[str, Section]:
        if self._sections is None or self.has_changed is True:
            self.reload()
        return self._sections

    def reload(self) -> None:
        if self.disable_read_event.is_set() is True:
            return
        with self.lock:
            self.load()

    def set_value(self, section_name: str, entry_key: str, entry_value: str, create_missing_section: bool = False) -> bool:
        success = super().set_value(section_name, entry_key, entry_value, create_missing_section=create_missing_section)
        self._do_auto_write(success)
        return success

    def add_entry(self, section_name: str, entry: Entry, create_missing_section: bool = False) -> bool:
        success = super().add_entry(section_name, entry, create_missing_section=create_missing_section)
        self._do_auto_write(success)
        return success

    def add_section(self, section, existing_ok: bool = True) -> None:
        success = super().add_section(section, existing_ok=existing_ok)
        self._do_auto_write(success)
        return success

    def remove_entry(self, section_name: str, entry_key: str, missing_ok: bool = False) -> bool:
        success = super().remove_entry(section_name, entry_key, missing_ok=missing_ok)
        self._do_auto_write(success)
        return success

    def remove_section(self, section_name: str, missing_ok: bool = False) -> bool:
        success = super().remove_section(section_name, missing_ok=missing_ok)
        self._do_auto_write(success)
        return success

    def clear_all_sections(self) -> bool:
        success = super().clear_all_sections()
        self._do_auto_write(success)
        return success

    def clear_entries(self, section_name: str, missing_ok: bool = False) -> bool:
        success = super().clear_entries(section_name, missing_ok=missing_ok)
        self._do_auto_write(success)
        return success

    def save(self) -> None:
        with self.lock:
            sections = self.sections.copy()
            sections.pop(self.env_section.name)
            data = '\n\n'.join(section.as_text() for section in sections.values())

            self.write(data)

    def load(self) -> None:
        with self.lock:
            content = self.read()
            self._sections = {section.name: section for section in self.parser.parse(content)} | {self.env_section.name: self.env_section}
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
