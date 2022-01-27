import unittest

from syngenta_digital_dta.common import schema_mapper


class SchemaMapperTest(unittest.TestCase):

    def test_map_to_schema(self):
        data = {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        results = schema_mapper.map_to_schema(
            data, 'tests/openapi.yml', 'test-dynamo-model')
        self.assertDictEqual(results, data)

    def test_map_to_schema_ignore(self):
        data = {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'ignore_key': True,
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': [1, 2, 3],
            'array_objects': [
                {
                    'array_string_key': 'a',
                    'array_number_key': 1
                }
            ],
            'created': '2020-10-05',
            'modified': '2020-10-05'
        }
        results = schema_mapper.map_to_schema(data, 'tests/openapi.yml', 'test-dynamo-model')
        data.pop('ignore_key', None)
        self.assertDictEqual(results, data)

    def test_map_to_schema_empty(self):
        data = {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            }
        }
        results = schema_mapper.map_to_schema(data, 'tests/openapi.yml', 'test-dynamo-model')
        self.assertDictEqual(results, {
            'test_id': 'abc456',
            'test_query_id': 'def789',
            'object_key': {
                'string_key': 'nothing'
            },
            'array_number': None,
            'array_objects': [],
            'created': None,
            'modified': None}
        )
