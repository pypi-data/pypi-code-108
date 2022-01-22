from typing import Dict

from .name import NameFieldGenerator
from .schema import SchemaFieldGenerator
from .base import FieldGenerator
from .number import NumberFieldGenerator
from .date import DateFieldGenerator
from .country import CountryFieldGenerator
from .reference import *

generators: Dict[str, FieldGenerator] = {
    "number": NumberFieldGenerator,
    "date": DateFieldGenerator,
    "country": CountryFieldGenerator,
    "name": NameFieldGenerator
}


def getGeneratorFromFieldType(field_type: str, field_options: Dict[str, str]) -> FieldGenerator:
    Generator = generators.get(field_type, SchemaFieldGenerator)

    return Generator(field_options, field_type)


def get_schema_by_id(id: int, schema_name: str, res: Dict = {}, iter_res={}):
    schema_list = iter_res.get(schema_name, res.get(schema_name))

    schema = list(filter(
        lambda entry: entry[0] == id, schema_list[1]))

    if len(schema) == 0:
        return None

    return schema[0]


def get_value_by_attr_name(attr_name: str, schema_name: str, res: Dict = {}, iter_res={}, id=None):
    schema = iter_res.get(schema_name, res.get(schema_name))
    if schema is None:
        raise Exception(
            f"Cannot find schema: '{schema_name}' in current result")

    entries = list(filter(
        lambda header: header[1][0] == attr_name, enumerate(schema[0])))

    if len(entries) == 0:
        raise Exception(f"Cannot find attribute: '{attr_name}'")

    entry = entries[0]

    # check if the entry is a schema field generator
    generator = getattr(entry[1][1], "__self__", None)
    if generator is not None and isinstance(generator, SchemaFieldGenerator):
        # find the referenced schema
        return generator.schema

    if id is None:
        return schema[1][-1][entry[0]]
    else:
        entries = list(
            filter(lambda entry: entry[0] == id, schema[1]))

        if len(entries) == 0:
            raise Exception(f"Could not find entry with id '{id}'")

        return entries[0][entry[0]]
