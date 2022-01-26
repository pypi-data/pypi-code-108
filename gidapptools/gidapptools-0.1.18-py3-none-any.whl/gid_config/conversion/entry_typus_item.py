"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Any, Union
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_config.enums import SpecialTypus

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@attr.s(auto_attribs=True, auto_detect=True, slots=True)
class EntryTypus:
    original_value: str = attr.ib(on_setattr=attr.setters.NO_OP, default=None)
    base_typus: type = attr.ib(on_setattr=attr.setters.NO_OP, default=SpecialTypus.DELAYED)
    named_arguments: dict[str, Any] = attr.ib(default=None, converter=attr.converters.default_if_none(factory=dict))

    def __hash__(self) -> int:
        return hash(self.base_typus)

    def __getitem__(self, key: Union[str, int]) -> Any:
        if isinstance(key, int):
            return self.other_arguments[key]

        return self.named_arguments[key]

    def get(self, key: Union[str, int], default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: Union[str, int], default: Any = None) -> Any:
        if isinstance(key, int):
            return self.other_arguments.pop(key, default)
        return self.named_arguments.pop(key, default)

    def __repr__(self) -> str:
        if self.base_typus is SpecialTypus.DELAYED:
            return f"{self.base_typus.name}(original_value={self.original_value!r})"
        text = f"{self.base_typus}"
        if self.named_arguments:
            text += "(" + ', '.join(f"{key}={value}" for key, value in self.named_arguments.items()) + ')'
        return text

    @property
    def typus(self) -> type:
        sub_typus = [item for item in self.named_arguments.values() if isinstance(item, EntryTypus)]
        if sub_typus:
            sub_typus = sub_typus[0]
            return self.base_typus[sub_typus.typus]
        return self.base_typus

    @classmethod
    @property
    def special_name_conversion_table(cls) -> str:
        return {'str': 'string',
                'int': 'integer',
                'bool': 'boolean'}

    def convert_for_json(self) -> str:

        if self.original_value is not None:
            return self.original_value
        _out = self.base_typus.__name__
        _out = self.special_conversion_map.get(_out, _out)
        args = ''
        if self.named_arguments:
            args = ', '.join(value for value in self.named_arguments.values())

        if args:
            _out += f"({args})"
        return _out


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
