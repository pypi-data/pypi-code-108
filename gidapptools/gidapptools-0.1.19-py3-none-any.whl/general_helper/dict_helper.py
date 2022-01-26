"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import re
import inspect
from typing import Any, Union, Mapping, Callable, Hashable, Iterable, Optional, Generator
from pathlib import Path
from threading import Lock
from collections import UserDict, namedtuple

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import KeyPathError, NotMappingError, AdvancedDictError, DictMergeConflict
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.general_helper.checker import is_hashable

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def replace_dict_keys(in_dict: dict, *replacement_pairs: tuple[Hashable, Hashable]) -> dict:
    # replacement_table = {item[0]: item[1] for item in replacement_pairs}
    # return in_dict.__class__(**{replacement_table.get(k, k): v for k, v in in_dict.items()})

    for old_key, new_key in replacement_pairs:
        if old_key in in_dict:
            in_dict[new_key] = in_dict.pop(old_key)

    return in_dict


def get_by_keypath(the_dict: dict, key_path: list[str], default: Any = None, *, strict: bool = False) -> Any:
    key_path = key_path.copy()
    last_key = key_path.pop(-1)
    for key in key_path:
        try:
            the_dict = the_dict[key]
        except KeyError as e:
            if strict is True:
                raise KeyError(f"The {key_path.index(key)+1}. key {key!r} was not found in the dict.") from e
            return default
    return the_dict.get(last_key, default)


def set_by_key_path(the_dict: dict, key_path: list[str], value: Any, *, create_intermediates: bool = False) -> None:
    key_path = key_path.copy()
    last_key = key_path.pop(-1)
    for key in key_path:
        try:
            the_dict = the_dict[key]
        except KeyError as e:
            if create_intermediates is True:
                the_dict[key] = {}
                the_dict = the_dict[key]
            else:
                raise KeyError(f"The {key_path.index(key)+1}. key {key!r} was not found in the dict, use 'create_intermediates=True' to auto-create intermediated keys if missing.") from e

    the_dict[last_key] = value


def multiple_dict_get(key: Hashable, *dictionaries, final_default: Any = None) -> Any:
    for _dict in dictionaries:
        value = _dict.get(key, MiscEnum.NOT_FOUND)
        if value is not MiscEnum.NOT_FOUND:
            return value
    return final_default


def multiple_dict_pop(key: Hashable, *dictionaries, final_default: Any = None) -> Any:
    for _dict in dictionaries:
        value = _dict.pop(key, MiscEnum.NOT_FOUND)
        if value is not MiscEnum.NOT_FOUND:
            return value
    return final_default


RAW_KEYPATH_TYPE = Union[list[str], str, Hashable]
MODDIFIED_KEYPATH_TYPE = list[Hashable]

ResolveKeyPathResult = namedtuple("ResolveKeyPathResult", ["data", "last_key"], defaults=(None,))


class AdvancedDict(UserDict):
    empty_values = [[], "", set(), tuple(), frozenset(), dict(), b"", None]

    def __init__(self,
                 data: Mapping = None,
                 keypath_separator: str = '.',
                 case_insensitive: bool = False,
                 convert_keys_to_str: bool = False,
                 auto_set_missing: bool = False,
                 empty_is_missing: bool = False,
                 extra_empty_values: Iterable[Any] = None) -> None:
        self.keypath_separator = keypath_separator
        self._case_insensitive = case_insensitive
        self.auto_set_missing = auto_set_missing
        self.convert_keys_to_str = convert_keys_to_str
        self.empty_is_missing = empty_is_missing
        if extra_empty_values is not None:
            self.empty_values.extend(extra_empty_values)
        self._data = data

    @property
    def data(self) -> dict:
        return self._data

    @property
    def case_insensitive(self) -> bool:
        return self._case_insensitive

    def _modify_key(self, key: Hashable) -> Hashable:

        if self.convert_keys_to_str is True and not isinstance(key, str):
            key = str(key)
        if self.case_insensitive is True and isinstance(key, str):
            return key.casefold()
        if not is_hashable(key):
            # TODO: better custom error
            raise TypeError(f"unhashable key {key!r} in key_path.")
        return key

    def _handle_keypath(self, key_path: RAW_KEYPATH_TYPE) -> MODDIFIED_KEYPATH_TYPE:
        if not isinstance(key_path, (str, Iterable)):
            return [self._modify_key(key_path)]

        if isinstance(key_path, str):
            key_path = key_path.split(self.keypath_separator)

        new_key_path = [self._modify_key(key) for key in key_path]

        return new_key_path

    def _resolve_key_path(self, key_path: MODDIFIED_KEYPATH_TYPE, *, hold_last: bool = False, check_auto_set: bool = False) -> ResolveKeyPathResult:
        data = self.data
        key_path = self._handle_keypath(key_path)
        last_key = None if hold_last is False else key_path.pop(-1)
        for key in key_path:
            try:
                if not isinstance(data, Mapping):
                    raise NotMappingError(key, data, key_path, 'get', last_key)
                data = data[key]
            except KeyError as error:
                if check_auto_set is True and self.auto_set_missing is True:
                    data[key] = {}
                    data = data[key]
                else:
                    raise KeyPathError(key, key_path, last_key) from error

        return ResolveKeyPathResult(data, last_key)

    def __getitem__(self, key_path: RAW_KEYPATH_TYPE) -> Any:
        result = self._resolve_key_path(key_path).data
        if self.empty_is_missing is True and result in self.empty_values:
            raise KeyPathError(key_path[-1], key_path)
        return result

    def __setitem__(self, key_path: RAW_KEYPATH_TYPE, value: Any) -> None:
        data, last_key = self._resolve_key_path(key_path, hold_last=True, check_auto_set=True)
        if not isinstance(data, Mapping):
            raise NotMappingError(last_key, data, self._handle_keypath(key_path), 'set')
        data[last_key] = value

    def set(self, key_path: RAW_KEYPATH_TYPE, value: Any) -> None:
        self.__setitem__(key_path=key_path, value=value)

    def __delitem__(self, key_path: RAW_KEYPATH_TYPE) -> None:
        data, last_key = self._resolve_key_path(key_path, hold_last=True)
        del data[last_key]

    def update(self, data: Mapping = None, **kwargs) -> None:
        data = {} if data is None else data
        update_data = {self._modify_key(key): value for key, value in data.items()}
        update_kwargs = {self._modify_key(key): value for key, value in kwargs.items()}
        super().update(update_data, **update_kwargs)

    # pylint: disable=arguments-renamed
    def get(self, key_path: Any, default: Any = None) -> Any:
        try:
            return self[key_path]
        except (KeyError, AdvancedDictError):
            return default

    def walk(self, temp_copy: bool = False) -> Generator[tuple[tuple[str], Any], None, None]:

        def _walk(data: dict[Hashable, Any], path: list[str] = None) -> Generator[tuple[tuple[str], Any], None, None]:
            path = [] if path is None else path
            for key, value in data.items():

                temp_path = path + [key]
                if isinstance(value, (self.__class__, dict, Mapping)):
                    yield from _walk(value, temp_path)
                else:

                    yield temp_path, value

        _data = self.data if temp_copy is False else self.data.copy()
        yield from _walk(_data)

    def modify_with_visitor(self, visitor: "BaseVisitor") -> None:
        for key_path, value in self.walk(temp_copy=True):
            visitor.visit(self, key_path, value)


class BaseVisitor:
    handle_prefix = "_handle_"
    handler_regex = re.compile(rf"^{handle_prefix}(?P<target>\w+)$")
    named_args_doc_identifier = "NAMED_VALUE_ARGUMENTS"

    def __init__(self, extra_handlers: dict[Hashable, Callable] = None, default_handler: Callable = None) -> None:
        self.extra_handlers = {} if extra_handlers is None else extra_handlers
        self.default_handler = default_handler
        self._handlers: dict[Hashable, Callable] = None
        self._inspect_lock = Lock()

    def reload(self) -> None:
        self._collect_handlers()

    def _validate_new_handler(self, handle_func: Callable) -> bool:
        # TODO: add validation logic.
        return True

    def add_handler(self, target_name: str, handler: Callable) -> None:
        # TODO: make it possible to inject self, or decide if.
        if self._validate_new_handler(handler) is True:
            self.extra_handlers[target_name] = handler

    def set_default_handler(self, handler: Callable):
        self.add_handler(MiscEnum.DEFAULT, handler)

    @classmethod
    def get_all_handler_names(cls) -> tuple[str]:
        instance = cls(AdvancedDict())
        return tuple(instance.handlers)

    @classmethod
    def get_all_handlers_with_named_arguments(cls) -> dict[str, Optional[dict[str, str]]]:
        def get_named_args(text: str) -> dict[str, str]:
            _named_args = {}
            named_args_index = text.find(cls.named_args_doc_identifier)
            next_line_index = text.find('\n', named_args_index)
            if named_args_index == -1:
                return _named_args
            gen = (line for line in text[next_line_index:].splitlines() if line)
            line = next(gen)
            while line.startswith('\t') or line.startswith(' ' * 4):
                line = line.strip()
                if not line:
                    continue
                if line in {"Returns:", "Args:"}:
                    break
                if line.strip().casefold == 'none':
                    return _named_args

                name, description = line.split(':')
                _named_args[name.strip()] = description.strip()

                line = next(gen, '')
            return _named_args

        instance = cls(AdvancedDict())
        _out = {}
        for handler_name, handler_obj in instance.handlers.items():
            doc_text = handler_obj.__doc__
            if doc_text is None:
                _out[handler_name] = {}
            else:
                _out[handler_name] = get_named_args(doc_text)
        return _out

    @property
    def handlers(self) -> dict[Hashable, Callable]:
        if self._inspect_lock.locked() is True:
            return
        if self._handlers is None:
            self._collect_handlers()
        return self._handlers

    def _collect_handlers(self) -> None:
        with self._inspect_lock:
            collected_handlers = {}
            for meth_name, meth_obj in inspect.getmembers(self, inspect.ismethod):

                match = self.handler_regex.match(meth_name)
                if match:
                    target = match.group('target')
                    if not target.strip():
                        continue
                    if target == 'default':
                        target = MiscEnum.DEFAULT
                        if self.default_handler is None:
                            self.default_handler = meth_obj

                    collected_handlers[target] = meth_obj
            if self._handlers is None:
                self._handlers = {}
            self._handlers |= collected_handlers
            self._handlers |= self.extra_handlers

    def _modify_value(self, value: Any) -> Any:
        return value

    def visit(self, in_dict: Union["AdvancedDict", dict], key_path: tuple[str], value: Any) -> None:

        key_path = tuple(key_path)
        value_key = self._modify_value(value)

        handler = self.handlers.get(key_path, self.handlers.get(value_key, self.default_handler))
        if handler is None:
            return
        if isinstance(in_dict, AdvancedDict):
            in_dict.set(key_path, handler(value))
        else:
            set_by_key_path(in_dict, key_path, handler(value))


class SafeMergeDict(UserDict):
    extra_none_values: set[Any] = set()

    def __init__(self, __dict=None, raise_on_overwrite: bool = False, **kwargs) -> None:
        self.data = {} if __dict is None else __dict
        self.data |= kwargs
        self.raise_on_overwrite = raise_on_overwrite

    @classmethod
    def add_none_value(cls, none_value: Any) -> None:
        cls.extra_none_values.add(none_value)

    @classmethod
    def remove_none_value(cls, none_value: Any) -> None:
        if none_value in cls.extra_none_values:
            cls.extra_none_values.remove(none_value)

    @property
    def none_values(self) -> set[Any]:
        return {None}.union(self.extra_none_values)

    def safe_merge(self, first_dict: dict, second_dict: dict) -> dict:
        if all(key not in first_dict for key in second_dict):
            return self.__class__(first_dict | second_dict)
        new_dict = first_dict.copy()
        for key, value in second_dict.items():
            print(key)
            if key not in new_dict or new_dict[key] in self.none_values:
                new_dict[key] = value
            elif self.raise_on_overwrite is True:
                raise DictMergeConflict(first_dict=first_dict, second_dict=second_dict, conflicting_key=key, none_values=self.none_values)
        return self.__class__(new_dict)

    def __or__(self, other):
        if isinstance(other, UserDict):
            return self.safe_merge(self.data, other.data)
        if isinstance(other, dict):
            return self.safe_merge(self.data, other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, UserDict):
            return self.safe_merge(other.data, self.data)
        if isinstance(other, dict):
            return self.safe_merge(other, self.data)
        return NotImplemented

    def __ior__(self, other):
        if isinstance(other, UserDict):
            self.data = self.safe_merge(self.data, other.data)
        else:
            self.data = self.safe_merge(self.data, other)
        return self


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
