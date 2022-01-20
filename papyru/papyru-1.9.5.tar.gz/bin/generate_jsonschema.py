#!/usr/bin/env python3

import json
import sys
from functools import reduce
from os.path import join

import yaml


def _load_schemas_from_file(schema_file):
    with open(schema_file) as f:
        data = yaml.load(f.read(), Loader=yaml.SafeLoader)
    return data['components']['schemas']


def _load_ref(value, schemas, schemas_dir):
    custom_schema_file = value.split('#')[0]
    schema_to_load = value.split('/')[-1]
    if custom_schema_file == '':
        sub_schemas = schemas
    else:
        sub_schemas = _load_schemas_from_file(join(schemas_dir,
                                                   custom_schema_file))
    return _load_references(sub_schemas[schema_to_load],
                            sub_schemas,
                            schemas_dir)


def _load_list(schema, schemas, schemas_dir):
    for index, value in enumerate(schema):
        schema[index] = _load_references(value, schemas, schemas_dir)

    return schema


def _load_dict(schema, schemas, schemas_dir):
    for key in list(schema):
        if '$ref' in key:
            schema.update(_load_ref(schema[key], schemas, schemas_dir))
            del schema[key]
        elif key == 'enum' and 'items' in schema.keys():
            schema['items']['enum'] = schema['enum']
            del schema['enum']
        elif key == 'x-extensible-enum' and 'items' in schema.keys():
            schema['items']['enum'] = schema['x-extensible-enum']
            del schema['x-extensible-enum']
        elif key == 'x-extensible-enum':
            schema['enum'] = schema['x-extensible-enum']
            del schema['x-extensible-enum']
        else:
            schema[key] = _load_references(schema[key], schemas, schemas_dir)
    return schema


def _load_references(schema, schemas, schemas_dir):
    if type(schema) is list:
        schema = _load_list(schema, schemas, schemas_dir)
    elif type(schema) is dict:
        schema = _load_dict(schema, schemas, schemas_dir)
    return schema


def resolve_inheritance(schemas):
    if 'allOf' in schemas:
        def merge_dict_items(acc, el):
            key, value = el
            acc[key] = value
            return acc

        def merge_values(lhs, rhs):
            if isinstance(lhs, list):
                return list(set(lhs) | set(rhs))
            elif isinstance(lhs, dict):
                return reduce(merge_dict_items, lhs.items(), rhs)
            else:
                raise NotImplementedError()

        def combine_schemas(acc, el):
            for key, value in el.items():
                if key in acc:
                    acc[key] = merge_values(acc[key], value)
                else:
                    acc[key] = value
            return acc

        return reduce(combine_schemas, schemas['allOf'], {})
    else:
        return schemas


def main(argv):
    if len(argv) < 3:
        print('usage: %s SWAGGER_FILE OUTPUT_DIR' % argv[0])
        sys.exit(1)
    else:
        schemas_dir = argv[1].rsplit('/', 1)[0]
        schemas = _load_schemas_from_file(argv[1])
        for title, schema in schemas.items():
            json_schema = {
                **resolve_inheritance(
                    _load_references(schema, schemas, schemas_dir)),
                'additionalProperties': False
            }

            with open('%s/%s.json' % (argv[2], title),
                      'w') as of:
                of.write(json.dumps(json_schema, indent=2))


if __name__ == '__main__':
    main(sys.argv)
