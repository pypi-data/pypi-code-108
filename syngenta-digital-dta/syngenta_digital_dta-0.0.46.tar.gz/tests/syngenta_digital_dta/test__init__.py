import uuid
import unittest
import warnings


import syngenta_digital_dta

class AdapterTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None

    def test_dynamodb_adapter(self):
        ddb = syngenta_digital_dta.adapter(
            engine='dynamodb',
            table='TABLE_NAME',
            endpoint='http://localhost:4000',
            model_schema='test-dynamo-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='test_id',
            model_version_key='modified'
        )
        self.assertIsInstance(ddb, syngenta_digital_dta.DynamodbAdapter)

    def test_elasticseach_adapter(self):
        es = syngenta_digital_dta.adapter(
            engine='elasticsearch',
            index='users',
            endpoint='localhost',
            model_schema='test-elasticsearch-user-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='user_id',
            model_version_key='modified'
        )
        self.assertIsInstance(es, syngenta_digital_dta.ElasticsearchAdapter)

    def test_postgres_adapter(self):
        ps = syngenta_digital_dta.adapter(
            engine='postgres',
            table='users',
            endpoint='localhost',
            database='dta-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            model_schema='test-postgres-user-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='user_id',
            model_version_key='modified',
            relationships={
                'ADDRESSES_TABLE': 'user_id'
            }
        )
        self.assertIsInstance(ps, syngenta_digital_dta.PostgresAdapter)

    def test_redshift_adapter(self):
        ps = syngenta_digital_dta.adapter(
            engine='redshift',
            table='users',
            endpoint='localhost',
            database='dta-redshift',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            model_schema='test-redshift-user-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='user_id',
            model_version_key='modified',
            relationships={
                'ADDRESSES_TABLE': 'user_id'
            }
        )
        self.assertIsInstance(ps, syngenta_digital_dta.PostgresAdapter)

    def test_adapter_exception(self):
        try:
            syngenta_digital_dta.adapter(
                engine='not-supported'
            )
            self.assertEqual(True, False)
        except Exception as e:
            self.assertEqual(str(e), 'engine not-supported not supported; contribute to get it supported :)')
