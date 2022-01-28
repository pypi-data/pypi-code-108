import sys
from typing import Union, Dict

from tableschema import Schema
from tableschema.exceptions import LoadError

from tsfaker.exceptions import DescriptorLoadError, InvalidSchema, ResourceCycle
from tsfaker.io.utils import get_base_file_name

INPUT_DESCRIPTOR = 'input_descriptor'
OUTPUT_FILE = 'output_file'
NAME = 'name'


def read_schema(input_descriptor: Union[str, dict], output_file: str, ignore_foreign_keys: bool) -> Schema:
    try:
        if input_descriptor == '-':
            schema = Schema(sys.stdin)
        else:
            schema = Schema(input_descriptor)
    except LoadError:
        raise DescriptorLoadError("Impossible to load descriptor from '{}'".format(input_descriptor))

    if ignore_foreign_keys:
        schema.descriptor.pop('foreignKeys', None)

    schema.descriptor[INPUT_DESCRIPTOR] = input_descriptor
    schema.descriptor[OUTPUT_FILE] = output_file
    if NAME not in schema.descriptor:
        if output_file != '-':
            schema.descriptor[NAME] = get_base_file_name(output_file)
        elif input_descriptor != '-':
            schema.descriptor[NAME] = get_base_file_name(input_descriptor)
        else:
            schema.descriptor[NAME] = None

    if not schema.valid:
        raise InvalidSchema(schema, 'Input schema has the following errors : {}'.format(
            [str(error) for error in schema.errors]))

    schema.commit(strict=True)

    return schema


def iter_schemas_to_generate(resource_name_to_path_or_schema: Dict[str, Union[str, Schema]]):
    number_of_schemas = len(get_all_schemas_to_generate(resource_name_to_path_or_schema))
    for _ in range(number_of_schemas):
        for schema in get_all_schemas_to_generate(resource_name_to_path_or_schema):
            if is_possible_to_generate(schema, resource_name_to_path_or_schema):
                yield schema

    left_schemas = get_all_schemas_to_generate(resource_name_to_path_or_schema)
    if left_schemas:
        schemas_str = [schema.descriptor.get(NAME) + ':' + schema.descriptor.get(INPUT_DESCRIPTOR)
                       for schema in left_schemas]
        raise ResourceCycle("There is a cycle between the following schemas foreign keys : \n{}"
                            .format('\n'.join(schemas_str)))


def get_all_schemas_to_generate(resource_name_to_path_or_schema: Dict[str, Union[str, Schema]]):
    return [schema for schema in resource_name_to_path_or_schema.values() if isinstance(schema, Schema)]


def is_possible_to_generate(schema, resource_name_to_path_or_schema):
    result = True
    for foreign_key in schema.foreign_keys:
        resource_name = foreign_key['reference']['resource']
        if isinstance(resource_name_to_path_or_schema[resource_name], Schema):
            result = False
    return result
