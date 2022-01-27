import uuid
import unittest
import warnings

import syngenta_digital_dta
from syngenta_digital_dta.elasticsearch import es_mapper
from tests.syngenta_digital_dta.elasticsearch import mocks

class ESMapperTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None
        self.es_mapper_adapter = syngenta_digital_dta.adapter(
            engine='elasticsearch',
            index='company',
            endpoint='localhost',
            model_schema='test-es-mapper-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='company_id',
            model_version_key='modified'
        )

    def test_convert_schema_to_mapping(self):
        mapping = es_mapper.convert_schema_to_mapping('tests/openapi.yml', 'test-es-mapper-model')
        self.assertDictEqual(mapping, mocks.get_mapping())

    def test_convert_schema_to_mapping_with_special(self):
        mapping = es_mapper.convert_schema_to_mapping('tests/openapi.yml', 'test-es-mapper-model', {'company_name': 'keyword'})
        self.assertDictEqual(mapping, mocks.get_mapping('keyword'))

    def test_convert_schema_to_mapping_with_special_multiple_shared_keys(self):
        mapping = es_mapper.convert_schema_to_mapping('tests/openapi.yml', 'test-es-mapper-model', {'shared': 'keyword'})
        self.assertDictEqual(mapping, mocks.get_mapping())

    def test_convert_schema_template_will_be_accepted_by_elasticsearch(self):
        try:
            self.es_mapper_adapter.create_template(
                name='company',
                index_patterns='company-*'
            )
            self.assertEqual(True, True)
        except Exception as e:
            print(e)
            self.assertEqual(False, True)

    def test_convert_schema_index_will_be_accepted_by_elasticsearch(self):
        try:
            self.es_mapper_adapter.create_index()
            self.assertEqual(True, True)
        except Exception as e:
            print(e)
            self.assertEqual(False, True)
