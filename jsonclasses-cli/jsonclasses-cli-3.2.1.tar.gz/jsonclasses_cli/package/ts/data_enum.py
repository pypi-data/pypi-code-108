from enum import Enum
from inflection import camelize
from jsonclasses_cli.package.ts.interface_enum import interface_enum, interface_enum_item


def data_enum(enum: type[Enum]) -> str:
    return interface_enum(enum.__name__, map(_data_enum_item, enum))


def _data_enum_item(option: Enum):
    name = camelize(option.name.lower())
    value = option.name
    return interface_enum_item(name, value)
