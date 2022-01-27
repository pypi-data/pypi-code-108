import unittest
import warnings

from syngenta_digital_dta.common.base_adapter import BaseAdapter


class BaseAdapterTest(unittest.TestCase):

    def setUp(self, *args, **keywargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None
        self.mock_sns_arn = 'arn:aws:sns:us-east-2:111111111111:unittest-mock-sns-topic'

    def test_publish(self):
        kwargs = {
            'model_schema': 'test-dynamo-model',
            'model_identifier': 'test_id',
            'model_version_key': 'modified',
            'author_identifier': 'unit-test',
            'sns_default_attributes': True,
            'sns_arn': self.mock_sns_arn
        }
        try:
            base_adapter = BaseAdapter(**kwargs)
            base_adapter.publish('unit-test', {'unit-test': True})
            self.assertEqual(True, True)
        except:
            self.assertEqual(False, True)

    def test_publish_default_attributes(self):
        kwargs = {
            'model_schema': 'test-dynamo-model',
            'model_identifier': 'test_id',
            'model_version_key': 'modified',
            'author_identifier': 'unit-test',
            'sns_default_attributes': True,
            'sns_arn': self.mock_sns_arn
        }
        base_adapter = BaseAdapter(**kwargs)
        result = base_adapter.create_format_attibutes('unit-test')
        self.assertDictEqual(
            result,
            {
                'model_schema': {
                    'DataType': 'String',
                    'StringValue': 'test-dynamo-model'
                },
                'model_identifier': {
                    'DataType': 'String',
                    'StringValue': 'test_id'
                },
                'model_version_key': {
                    'DataType': 'String',
                    'StringValue': 'modified'
                },
                'author_identifier': {
                    'DataType': 'String',
                    'StringValue': 'unit-test'
                },
                'operation': {
                    'DataType': 'String',
                    'StringValue': 'unit-test'
                }
            }
        )

    def test_publish_no_attributes(self):
        kwargs = {
            'model_schema': 'test-dynamo-model',
            'model_identifier': 'test_id',
            'model_version_key': 'modified',
            'author_identifier': 'unit-test',
            'sns_default_attributes': False,
            'sns_arn': self.mock_sns_arn
        }
        base_adapter = BaseAdapter(**kwargs)
        result = base_adapter.create_format_attibutes('unit-test')
        self.assertDictEqual(result, {})

    def test_publish_custom_attributes(self):
        kwargs = {
            'model_schema': 'test-dynamo-model',
            'model_identifier': 'test_id',
            'model_version_key': 'modified',
            'author_identifier': 'unit-test',
            'sns_default_attributes': False,
            'sns_arn': self.mock_sns_arn,
            'sns_attributes': {
                'unit_test': 'passed'
            }
        }
        base_adapter = BaseAdapter(**kwargs)
        result = base_adapter.create_format_attibutes('unit-test')
        self.assertDictEqual(
            result,
            {
                'unit_test': {
                    'DataType': 'String',
                    'StringValue': 'passed'
                }
            }
        )

    def test_publish_custom_attributes_number(self):
        kwargs = {
            'model_schema': 'test-dynamo-model',
            'model_identifier': 'test_id',
            'model_version_key': 'modified',
            'author_identifier': 'unit-test',
            'sns_default_attributes': False,
            'sns_arn': self.mock_sns_arn,
            'sns_attributes': {
                'unit_test': 1
            }
        }
        base_adapter = BaseAdapter(**kwargs)
        result = base_adapter.create_format_attibutes('unit-test')
        self.assertDictEqual(
            result,
            {
                'unit_test': {
                    'DataType': 'Number',
                    'StringValue': 1
                }
            }
        )

    def test_publish_combined_attributes(self):
        kwargs = {
            'model_schema': 'test-dynamo-model',
            'model_identifier': 'test_id',
            'model_version_key': 'modified',
            'author_identifier': 'unit-test',
            'sns_default_attributes': True,
            'sns_arn': self.mock_sns_arn,
            'sns_attributes': {
                'unit_test': 'passed'
            }
        }
        base_adapter = BaseAdapter(**kwargs)
        result = base_adapter.create_format_attibutes('unit-test')
        self.assertDictEqual(
            result,
            {
                'unit_test': {
                    'DataType': 'String',
                    'StringValue': 'passed'
                },
                'model_schema': {
                    'DataType': 'String',
                    'StringValue': 'test-dynamo-model'
                },
                'model_identifier': {
                    'DataType': 'String',
                    'StringValue': 'test_id'
                },
                'model_version_key': {
                    'DataType': 'String',
                    'StringValue': 'modified'
                },
                'author_identifier': {
                    'DataType': 'String',
                    'StringValue': 'unit-test'
                },
                'operation': {
                    'DataType': 'String',
                    'StringValue': 'unit-test'
                }
            }
        )
