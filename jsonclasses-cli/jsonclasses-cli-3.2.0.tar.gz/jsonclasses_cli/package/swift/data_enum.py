from enum import Enum
from inflection import camelize
from .codable_enum import codable_enum, codable_enum_item


def data_enum(enum: type[Enum]) -> str:
    return codable_enum(enum.__name__, 'String', map(_data_enum_item, enum))


def _data_enum_item(option: Enum):
    name = camelize(option.name.lower())
    value = option.name
    return codable_enum_item(name, 'String', value)
