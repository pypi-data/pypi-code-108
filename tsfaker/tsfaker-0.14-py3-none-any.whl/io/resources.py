import os
from typing import List, Dict

from tableschema import Schema

from tsfaker.exceptions import ResourceMissing, ResourceConflict
from tsfaker.io.schema import NAME, INPUT_DESCRIPTOR
from tsfaker.io.utils import get_base_file_name, replace_dash


def process_resources(resources: List[str]) -> Dict:
    resource_name_to_path_or_schema = dict()
    for csv_file_path in expand_resource_directories(resources):
        if not os.path.exists(csv_file_path):
            raise ResourceMissing("Resource file '{}' does not exists.".format(csv_file_path))

        resource_name = get_base_file_name(csv_file_path)
        if resource_name in resource_name_to_path_or_schema:
            raise ResourceConflict("Conflict in resource '{}', which is present from sources '{}' and '{}'"
                                   .format(resource_name, resource_name_to_path_or_schema[resource_name],
                                           csv_file_path))
        resource_name_to_path_or_schema[resource_name] = csv_file_path
    return resource_name_to_path_or_schema


def add_schema_to_resources(resource_name_to_path_or_schema: Dict, schemas: List[Schema]) -> None:
    for schema in schemas:
        resource_name = schema.descriptor[NAME]
        if resource_name in resource_name_to_path_or_schema:
            existing = resource_name_to_path_or_schema[resource_name]
            existing = existing if isinstance(existing, str) else existing.descriptor['input_descriptor']
            raise ResourceConflict("Conflict for resource name: '{}'.\n"
                                   "Existing resource path or schema input descriptor path: '{}'\n"
                                   "New schema input descriptor path: '{}'"
                                   .format(resource_name, existing, schema.descriptor['input_descriptor'])
                                   )

        resource_name_to_path_or_schema[resource_name] = schema

    for schema in schemas:
        for foreign_key in schema.foreign_keys:
            resource_name = foreign_key['reference']['resource']
            if resource_name not in resource_name_to_path_or_schema:
                raise ResourceMissing("Resource '{}' is missing to generate schema '{}' from input descriptor '{}'"
                                      .format(resource_name,
                                              schema.descriptor.get(NAME),
                                              replace_dash(schema.descriptor.get(INPUT_DESCRIPTOR), 'STDIN'))
                                      )


def expand_resource_directories(resources):
    resources_file_paths = []
    for resource in resources:
        if os.path.isdir(resource):
            resources_file_paths += get_csv_files_path_in_directory(resource)
        else:
            resources_file_paths.append(resource)
    return resources_file_paths


def get_csv_files_path_in_directory(folder_path: str) -> List[str]:
    csv_files_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.lower().endswith('.csv'):
                csv_files_paths.append(file_path)
    return csv_files_paths
