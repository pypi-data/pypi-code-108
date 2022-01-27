import uuid
import unittest
import warnings

import syngenta_digital_dta


class RedshiftAdapterTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None
        ADDRESSES_TABLE='addresses'
        self.user_adapter = syngenta_digital_dta.adapter(
            engine='redshift',
            table='users',
            endpoint='localhost',
            database='dta-redshift',
            port=5439,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            model_schema='test-redshift-user-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='user_id',
            model_version_key='modified',
            relationships={
                f'{ADDRESSES_TABLE}': 'user_id'
            }
        )
        self.address_adapter = syngenta_digital_dta.adapter(
            engine='redshift',
            endpoint='localhost',
            database='dta-redshift',
            table=ADDRESSES_TABLE,
            port=5439,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            model_schema='test-redshift-address-model',
            model_schema_file='tests/openapi.yml',
            model_identifier='address_id',
            model_version_key='modified'
        )
        self.user_adapter.connect()
        self.address_adapter.connect()
        self.__create_tables()

    def __create_tables(self):
        self.user_adapter.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id character varying(65000) PRIMARY KEY,
                email character varying(256),
                first character varying(256),
                last character varying(256)
            );
        """)
        self.user_adapter.cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS users_pkey ON users(user_id varchar_ops);
        """)
        self.user_adapter.cursor.execute("""
            CREATE TABLE IF NOT EXISTS addresses (
                address_id character varying(65000) PRIMARY KEY,
                user_id character varying(65000) REFERENCES users(user_id),
                address character varying(256),
                city character varying(256),
                state character varying(256),
                zipcode character varying(256)
            );
        """)
        self.user_adapter.cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS addresses_pkey ON addresses(address_id varchar_ops);
        """)
        self.user_adapter.commit()

    def test_init(self):
        self.assertIsInstance(self.user_adapter, syngenta_digital_dta.PostgresAdapter)

    def test_connected(self):
        self.assertEqual(self.user_adapter.connection.closed, 0)

    def test_insert(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        result = self.user_adapter.insert(data=data, commit=True)
        self.assertDictEqual(data, result)

    def test_create(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        result = self.user_adapter.create(data=data, commit=True)
        self.assertDictEqual(data, result)

    def test_insert_remove_keys(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III',
            'extra_key': True
        }
        result = self.user_adapter.insert(data=data, commit=True)
        data.pop('extra_key', None)
        self.assertDictEqual(data, result)
        self.assertEqual(data.get('extra_key'), None)

    def test_unique_constraint(self):
        data = {
            'user_id': 'some-unique-thing',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        try:
            self.user_adapter.insert(data=data, commit=True)
        except Exception as error:
            self.assertEqual(str(error), 'row already exist with user_id = some-unique-thing')

    def test_update(self):
        data = {
            'user_id': 'some-update-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        data['last'] = 'Cruse'
        result = self.user_adapter.update(data=data, commit=True)
        self.assertDictEqual(data, result)

    def test_update_fail(self):
        data = {
            'user_id': 'some-update-guid-success',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        data['user_id'] = 'some-update-guid-fail'
        try:
            self.user_adapter.update(data=data, commit=True)
        except Exception as error:
            self.assertEqual(str(error), 'row does not exist with user_id = some-update-guid-fail')

    def test_upsert(self):
        data = {
            'user_id': 'some-non-unique-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        result = self.user_adapter.upsert(data=data, commit=True)
        self.assertDictEqual(data, result)

    def test_delete(self):
        data = {
            'user_id': 'some-delete-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        self.user_adapter.delete('some-delete-guid', commit=True)

    def test_read(self):
        data = {
            'user_id': 'some-read-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        result = self.user_adapter.read('some-read-guid')
        self.assertDictEqual(data, result)

    def test_get(self):
        data = {
            'user_id': 'some-get-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True)
        result = self.user_adapter.read('some-get-guid')
        self.assertDictEqual(data, result)

    def test_get_with_debug(self):
        data = {
            'user_id': 'some-get-debug-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=data, commit=True, debug=True)
        result = self.user_adapter.read('some-get-debug-guid')
        self.assertDictEqual(data, result)

    def test_get_fail(self):
        result = self.user_adapter.read('some-get-fail-guid')
        self.assertEqual(None, result)

    def test_get_all(self):
        last = str(uuid.uuid4())
        data_list = []
        data = {
            'email': 'paul.cruse@syngenta.com',
            'first': 'Get',
            'last': 'Cruse III'
        }
        for count in [0,1,2,3]:
            data['user_id'] = 0
            data['user_id'] = str(data['user_id'] + count)
            data['last'] = last
            data_list.append(data)
            self.user_adapter.upsert(data=data, commit=True)
        results = self.user_adapter.read_all(
            where={
                'first': 'Get',
                'last': last,
            },
            limit=2,
            offset=1
        )
        self.assertEqual(str(1), results[0]['user_id'])
        self.assertEqual(str(2), results[1]['user_id'])

    def test_get_all_fail(self):
        results = self.user_adapter.read_all(
            where={
                'first': 'fail'
            }
        )
        self.assertEqual([], results)

    def test_get_all_still_runs_without_addons(self):
        results = self.user_adapter.read_all(
            where=None,
            limit=None,
            offset=None
        )
        self.assertEqual(True, True)

    def test_relationship(self):
        user_data = {
            'user_id': 'some-user-relationship-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        address_data = {
            'address_id': 'some-address-guid',
            'user_id': 'some-user-relationship-guid',
            'address': '400 Street',
            'city': 'Chicago',
            'state': 'IL',
            'zipcode': '60616'
        }
        self.user_adapter.upsert(data=user_data, commit=True)
        self.address_adapter.upsert(data=address_data, commit=True)
        results = self.user_adapter.get_relationship('addresses', where={'user_id': 'some-user-relationship-guid'})
        self.assertEqual('some-user-relationship-guid', results[0]['user_id'])

    def test_query(self):
        user_data = {
            'user_id': 'some-query-relationship-guid',
            'email': 'paul.cruse@syngenta.com',
            'first': 'Paul',
            'last': 'Cruse III'
        }
        self.user_adapter.upsert(data=user_data, commit=True)
        results = self.user_adapter.query(
            query='SELECT * FROM users WHERE user_id = %(identifier_value)s',
            params={
                'identifier_value':'some-query-relationship-guid'
            }
        )
        self.assertEqual('some-query-relationship-guid', results[0]['user_id'])

    def test_query_readonly_constraint(self):
        try:
            results = self.user_adapter.query(
                query='DELETE FROM users WHERE user_id = %(identifier_value)s',
                params={
                    'identifier_value':'some-query-relationship-guid'
                }
            )
        except Exception as error:
            self.assertEqual(str(error), 'query method is for read-only operations; please use another function for destructive operatins')

    def test_query_no_params_constraint(self):
        try:
            results = self.user_adapter.query(query='SELECT * FROM users WHERE user_id =1')
        except Exception as error:
            self.assertEqual(str(error), 'params kwargs are required to prevent sql inject; send empty dict if not needed')
