"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import inspect
from typing import Union, Mapping, Callable, Hashable, Iterable
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class dispatch_mark:
    """
    Marks a method as a dispatch function for an instance `BaseDispatchTable`.
    """
    key_attribute_name: str = '_dispatch_key'
    alias_attribute_name: str = '_dispatch_aliases'
    DEFAULT = MiscEnum.DEFAULT

    def __init__(self, dispatch_key: Hashable = None, aliases: Iterable[Hashable] = None):
        self.dispatch_key = dispatch_key
        self.aliases = aliases

    def __call__(self, func: Callable):
        dispatch_key = func.__name__ if self.dispatch_key is None else self.dispatch_key
        aliases = [] if self.aliases is None else self.aliases
        setattr(func, self.key_attribute_name, dispatch_key)
        setattr(func, self.alias_attribute_name, aliases)

        return func


class BaseDispatchTable:
    DEFAULT = MiscEnum.DEFAULT
    mark = dispatch_mark

    def __init__(self,
                 instance: object = None,
                 auto_collect_prefix: str = None,
                 extra_dispatch: Mapping[Hashable, Callable] = None,
                 default_dispatch: Callable = None,
                 key_conversion: Union[Mapping, Callable] = None,
                 aliases: Mapping[Hashable, Hashable] = None) -> None:
        """
        [summary]

        [extended_summary]

        Args:
            instance (object, optional): [description]. Defaults to None.
            auto_collect_prefix (str, optional): [description]. Defaults to None.
            extra_dispatch (Mapping[Hashable, Callable], optional): [description]. Defaults to None.
            default_dispatch (Callable, optional): [description]. Defaults to None.
            key_conversion (Union[Mapping, Callable], optional): [description]. Defaults to None.
            aliases (Mapping[Hashable, Hashable], optional): [description]. Defaults to None.
        """
        self.instance = instance
        self.auto_collect_prefix = auto_collect_prefix
        self.extra_dispatch = {} if extra_dispatch is None else extra_dispatch
        self._table: dict[Hashable, Callable] = None
        self.default_dispatch: Callable = default_dispatch
        self._aliases = {} if aliases is None else aliases
        if key_conversion is None:
            self.key_conversion = lambda x: x
        elif isinstance(key_conversion, Mapping):
            self.key_conversion = lambda x: key_conversion.get(x, x)
        else:
            self.key_conversion = key_conversion

    def set_default_dispatch(self, value: Callable) -> None:
        self.default_dispatch = value
        self._table[dispatch_mark.DEFAULT] = value

    def _collect_dispatch_data(self) -> None:
        instance = self if self.instance is None else self.instance
        collected_data = {}
        for meth_name, meth_obj in inspect.getmembers(instance, inspect.ismethod):
            if self.auto_collect_prefix is not None and meth_name.startswith(self.auto_collect_prefix):
                key = self.key_conversion(meth_name.removeprefix(self.auto_collect_prefix))
                collected_data[key] = meth_obj

            key = self.key_conversion(getattr(meth_obj, dispatch_mark.key_attribute_name, None))
            if key in self._aliases:
                raise KeyError(f'An alias cannot be the same as a dispatch key, {key=!r}')
            if key is dispatch_mark.DEFAULT and self.default_dispatch is None:
                self.default_dispatch = meth_obj
            if key is not None:
                collected_data[key] = meth_obj
                aliases = getattr(meth_obj, dispatch_mark.alias_attribute_name)
                for alias in aliases:
                    if alias in self._aliases:
                        raise KeyError(f"Alias {alias!r} already set in aliases.")
                    self._aliases[alias] = key

        self._table = collected_data

    def __getitem__(self, key: Hashable) -> Callable:
        if self._table is None:
            self._collect_dispatch_data()
        combined_table = self._table | self.extra_dispatch
        key = self._aliases.get(key, key)
        return combined_table[key]

    def __setitem__(self, key: Hashable, value: Callable) -> None:
        self.extra_dispatch[key] = value

    def get(self, key: Hashable, default=MiscEnum.NOTHING) -> Callable:
        try:
            return self[key]
        except KeyError:
            return self.default_dispatch if default is MiscEnum.NOTHING else default


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
