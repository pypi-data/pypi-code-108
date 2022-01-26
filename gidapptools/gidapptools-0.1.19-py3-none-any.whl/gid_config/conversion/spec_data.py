"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import json
from typing import Any, Union, Literal, Callable, Hashable, Optional
from pathlib import Path
from datetime import datetime, timedelta
from threading import RLock

# * Third Party Imports --------------------------------------------------------------------------------->
from yarl import URL

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.types import PATH_TYPE
from gidapptools.gid_config.enums import SpecAttribute
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.dict_helper import BaseVisitor, AdvancedDict, KeyPathError, set_by_key_path
from gidapptools.general_helper.string_helper import split_quotes_aware
from gidapptools.general_helper.mixins.file_mixin import FileMixin
from gidapptools.gid_config.conversion.conversion_table import EntryTypus
from gidapptools.gid_config.conversion.extra_base_typus import NonTypeBaseTypus

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class SpecVisitor(BaseVisitor):
    argument_regex = re.compile(r"(?P<base_type>\w+)\(((?P<sub_arguments>.*)\))?")
    sub_arguments_regex = re.compile(r"(?P<name>\w+)\s*\=\s*(?P<value>.*)")

    def __init__(self, extra_handlers: dict[Hashable, Callable] = None, default_handler: Callable = None, sub_argument_separator: str = ',') -> None:
        super().__init__(extra_handlers=extra_handlers, default_handler=default_handler)
        self.sub_argument_separator = sub_argument_separator

    def visit(self, in_dict: Union["AdvancedDict", dict], key_path: tuple[str], value: Any) -> None:

        key_path = tuple(key_path)

        if key_path[-1] != 'converter':
            return
        value_key = self._modify_value(value)

        handler = self.handlers.get(key_path, self.handlers.get(value_key, self.default_handler))
        if handler is None:
            return
        if isinstance(in_dict, AdvancedDict):
            in_dict.set(key_path, handler(value, self._get_sub_arguments(value)))
        else:
            set_by_key_path(in_dict, key_path, handler(value, self._get_sub_arguments(value)))

    def _modify_value(self, value: Any) -> Any:
        value = super()._modify_value(value)
        try:
            value = self.argument_regex.sub(r"\g<base_type>", value)
        except (AttributeError, TypeError):
            pass

        return value

    def _get_handler_direct(self, value: str) -> Callable:
        return self.handlers.get(value, self._handle_string)

    def _get_sub_arguments(self, value: str, default: dict[str:str] = None) -> dict[str:str]:

        def _get_key_value_from_part(in_part: str) -> dict[str, str]:
            sub_match = self.sub_arguments_regex.match(in_part)
            name = sub_match.group('name')
            value = sub_match.group('value')
            return {name.strip(): value.strip().strip('"' + "'").strip()}

        default = {} if default is None else default
        try:
            match = self.argument_regex.match(value)
            sub_arguments_string = match.groupdict().get("sub_arguments", default)
            sub_arguments = {}
            for part in split_quotes_aware(sub_arguments_string, quote_chars="'", strip_parts=True):
                try:
                    sub_arguments |= _get_key_value_from_part(part)
                except AttributeError:
                    continue
            if not sub_arguments:
                return default
            return sub_arguments
        except AttributeError:
            return default

    def _handle_default(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        handles all values that other handlers, can't or that raised an error while dispatching to handlers.

        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): The nodes value.

        Returns:
            EntryTypus: An `EntryTypus` with only an `original_value` and the base_typus set to `SpecialTypus.DELAYED)
        """
        return EntryTypus(original_value=value)

    def _handle_boolean(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=bool)

    def _handle_string(self, value: Any, sub_arguments: dict[str, str] = None) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        sub_arguments = sub_arguments or {}
        if "choices" in sub_arguments:
            sub_arguments["choices"] = [i.strip() for i in sub_arguments["choices"].split('|')]
        return EntryTypus(original_value=value, base_typus=str, named_arguments=sub_arguments)

    def _handle_integer(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=int)

    def _handle_float(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=float)

    def _handle_bytes(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=bytes)

    def _handle_list(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        Converts the value to `list` with optional sub_type (eg: `list[int]`).

        NAMED_VALUE_ARGUMENTS:
            subtype: The subtype of the list, defaults to `string`, can be any other handled type.
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        def _process_subtypus(in_sub_arguments: dict[str, str]) -> None:
            subtypus_string = sub_arguments.pop('sub_typus', 'string')
            subtypus = self._get_handler_direct(subtypus_string)(subtypus_string, {})
            in_sub_arguments['sub_typus'] = subtypus

        def _process_split_char(in_sub_arguments: dict[str, str]) -> None:
            if "split_char" not in in_sub_arguments:
                in_sub_arguments["split_char"] = ','
        _process_subtypus(sub_arguments)
        _process_split_char(sub_arguments)

        return EntryTypus(original_value=value, base_typus=list, named_arguments=sub_arguments)

    def _handle_datetime(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        [summary]

        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=datetime)

    def _handle_path(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=Path)

    def _handle_url(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """

        return EntryTypus(original_value=value, base_typus=URL)

    def _handle_file_size(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=NonTypeBaseTypus.FILE_SIZE)

    def _handle_timedelta(self, value: Any, sub_arguments: dict[str, str]) -> EntryTypus:
        """
        NAMED_VALUE_ARGUMENTS:
            None
        Args:
            value (Any): [description]

        Returns:
            EntryTypus: [description]
        """
        return EntryTypus(original_value=value, base_typus=timedelta)


class SpecData(AdvancedDict):
    default_visitor_class = SpecVisitor
    visit_lock = RLock()

    def __init__(self, visitor: SpecVisitor, **kwargs) -> None:
        self.visitor = visitor
        super().__init__(data=None, **kwargs)

    @property
    def data(self) -> dict:
        with self.visit_lock:
            return super().data

    def _get_section_default(self, section_name: str) -> EntryTypus:

        return self.get([section_name, '__default__', "converter"], str)

    def _get_entry_default(self, section_name: str, entry_key: str) -> Union[str, MiscEnum]:
        return self.get([section_name, entry_key, 'default'], MiscEnum.NOTHING)

    def get_entry_typus(self, section_name: str, entry_key: str) -> EntryTypus:
        try:
            return self[[section_name, entry_key, "converter"]]
        except KeyPathError as error:
            try:
                return self._get_section_default(section_name=section_name)
            except KeyPathError:
                raise error

    def get_verbose_name(self, section_name: str, entry_key: str = None) -> Optional[str]:
        if entry_key is None:
            return self.get([section_name, '__verbose_name__'], default=None)
        else:
            return self.get_spec_attribute(section_name=section_name, entry_key=entry_key, attribute=SpecAttribute.VERBOSE_NAME, default=None)

    def get_description(self, section_name: str, entry_key: str) -> str:
        return self.get(key_path=[section_name, entry_key, SpecAttribute.DESCRIPTION.value], default="")

    def get_gui_visible(self, section_name: str, entry_key: str) -> bool:
        return self.get_spec_attribute(section_name, entry_key, SpecAttribute.GUI_VISIBLE, default=True)

    def get_spec_attribute(self, section_name: str, entry_key: str, attribute: Union[SpecAttribute, str], default=None) -> Any:
        attribute = SpecAttribute(attribute) if isinstance(attribute, str) else attribute
        return self.get([section_name, entry_key, attribute.value], default=default)

    def set_typus_value(self, section_name: str, entry_key: str, typus_value: str) -> None:
        if section_name not in self:
            self[section_name] = {}
        self[section_name][entry_key] = typus_value

    def _resolve_values(self) -> None:
        self.modify_with_visitor(self.visitor)

    def reload(self) -> None:
        with self.visit_lock:
            self.visitor.reload()
            self._resolve_values()


class SpecFile(FileMixin, SpecData):
    def __init__(self, file_path: PATH_TYPE, visitor: SpecVisitor, changed_parameter: Union[Literal['size'], Literal['file_hash']] = 'size', **kwargs) -> None:
        super().__init__(visitor=visitor, file_path=file_path, changed_parameter=changed_parameter, ** kwargs)
        self._data = None
        self.spec_name = self.file_path.stem.casefold()

    @property
    def data(self) -> dict:
        if self._data is None or self.has_changed is True:
            self.load()
        return self._data

    def reload(self) -> None:
        self.load()

    def load(self) -> None:
        with self.lock:
            self._data = json.loads(self.read())
            super().reload()

    def save(self) -> None:
        with self.lock:
            json_data = json.dumps(self.data, indent=4, sort_keys=False, default=lambda x: x.convert_for_json())
            self.write(json_data)

    def set_typus_value(self, section_name: str, entry_key: str, typus_value: str) -> None:
        super().set_typus_value(section_name=section_name, entry_key=entry_key, typus_value=typus_value)
        self.save()

# class SpecDataFile(SpecData):

#     def __init__(self, in_file: Path, changed_parameter: str = 'size', ensure: bool = True, visitor_class: SpecVisitor = None, **kwargs) -> None:
#         super().__init__(visitor_class=visitor_class, **kwargs)

#         self.file_path = Path(in_file).resolve()
#         self.changed_parameter = changed_parameter
#         self.ensure = ensure
#         self.last_size: int = None
#         self.last_file_hash: str = None
#         self.data = None
#         self.lock = Lock()

#     @property
#     def has_changed(self) -> bool:
#         if self.changed_parameter == 'always':
#             return True
#         if self.changed_parameter == 'both':
#             if any([param is None for param in [self.last_size, self.last_file_hash]] + [self.last_size != self.size, self.last_file_hash != self.last_file_hash]):
#                 return True
#         if self.changed_parameter == 'size':
#             if self.last_size is None or self.size != self.last_size:
#                 return True
#         elif self.changed_parameter == 'file_hash':
#             if self.last_file_hash is None or self.file_hash != self.last_file_hash:
#                 return True
#         return False

#     def get_converter(self, key_path: Union[list[str], str]) -> EntryTypus:
#         with self.lock:
#             if self.data is None or self.has_changed is True:
#                 self.reload(locked=True)
#             return super().get_converter(key_path)

#     @property
#     def size(self) -> int:
#         return self.file_path.stat().st_size

#     @property
#     def file_hash(self) -> str:
#         _file_hash = blake2b()
#         with self.file_path.open('rb') as f:
#             for chunk in f:
#                 _file_hash.update(chunk)
#         return _file_hash.hexdigest()

#     def reload(self, locked: bool = False) -> None:
#         self.load(locked)
#         super().reload()

#     def _json_converter(self, item: Union[EntryTypus, type]) -> str:
#         try:
#             return item.convert_for_json()
#         except AttributeError:
#             return EntryTypus.special_name_conversion_table(type.__name__, type.__name__)

#     def load(self, locked: bool = False):
#         def _load():
#             with self.file_path.open('r', encoding='utf-8', errors='ignore') as f:
#                 return json.load(f)

#         if self.file_path.exists() is False and self.ensure is True:
#             self.write(locked=locked)
#         if locked is False:
#             with self.lock:
#                 self.data = _load()
#         else:
#             self.data = _load()

#     def write(self, locked: bool = False) -> None:
#         def _write():
#             with self.file_path.open('w', encoding='utf-8', errors='ignore') as f:
#                 data = {} if self.data is None else self.data
#                 json.dump(data, f, default=self._json_converter, indent=4, sort_keys=True)

#         if locked is False:
#             with self.lock:
#                 _write()
#         else:
#             _write()


# region[Main_Exec]

if __name__ == '__main__':
    pass
# endregion[Main_Exec]
