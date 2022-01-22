from random import randint
from typing import Dict
from schema import Schema

from .base import FieldGenerator


class SchemaFieldGenerator(FieldGenerator):
    option_schema = Schema({})

    def validate(self):
        self.option_schema.validate(self.options)

    def generate(self, schema_name: str = None, res: Dict = {}, iter_res: Dict = {}):
        schema = iter_res.get(self.type)
        if schema is not None:
            # choose latest
            index = -1
        else:
            # choose random
            schema = res.get(self.type)
            if schema is not None:
                index = randint(0, len(schema[1]) - 1)

        if schema is None:
            raise Exception(f"Schema '{self.type}' is not generated yet")

        self.schema = {}
        for i in range(len(schema[0])):
            self.schema[schema[0][i][0]] = schema[1][index][i]
        return schema[1][index][0]


def get_value_by_header(field_attr: str, schema_name: str, res: Dict = {}, iter_res={}):
    schema = iter_res.get(schema_name, res.get(schema_name))
    if schema is None:
        raise Exception(f"Cannot find schema: 'schema_name' in current result")

    entry = list(filter(
        lambda header: header[1][0] == field_attr, enumerate(schema[0])))[0]

    # check if the entry is a schema field generator
    generator = getattr(entry[1][1], "__self__", None)
    if generator is not None and isinstance(generator, SchemaFieldGenerator):
        # find the referenced schema
        return generator.schema

    return schema[1][-1][entry[0]]
