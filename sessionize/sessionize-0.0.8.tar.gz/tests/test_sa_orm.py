import unittest

import sqlalchemy as sa

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.utils.sa_orm import primary_keys, has_primary_key
from sessionize.utils.sa_orm import get_table, get_class, get_column


# primary_keys
class TestPrimaryKeys(unittest.TestCase):
    def primary_keys(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        keys = primary_keys(table)
        expected = ['id']
        self.assertEqual(keys, expected)

    def test_primary_keys_sqlite(self):
        self.primary_keys(sqlite_setup)

    def test_primary_keys_postgres(self):
        self.primary_keys(postgres_setup)

    def test_primary_keys_schema(self):
        self.primary_keys(postgres_setup, schema='local')
        

# has_primary_key
class TestHasPrimaryKey(unittest.TestCase):
    def has_primary_key(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        result = has_primary_key(table)
        expected = True
        self.assertEqual(result, expected)

    def test_has_primary_key_sqlite(self):
        self.has_primary_key(sqlite_setup)

    def test_has_primary_key_postgres(self):
        self.has_primary_key(postgres_setup)

    def test_has_primary_key_schema(self):
        self.has_primary_key(postgres_setup, schema='local')


# get_table
class TestGetTable(unittest.TestCase):
    def get_table(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        result = get_table('people', engine, schema=schema)
        expected = table
        self.assertEqual(type(result), type(expected))
        self.assertEqual(result.name, expected.name)

    def test_get_table_sqlite(self):
        self.get_table(sqlite_setup)

    def test_get_table_postgres(self):
        self.get_table(postgres_setup)

    def test_get_table_schema(self):
        self.get_table(postgres_setup, schema='local')


# TODO: get_class tests
class TestGetClass(unittest.TestCase):
    def get_class(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        result = get_class('people', engine, schema=schema)
        self.assertEqual(result.name, 'people')

    #def test_get_class_sqlite(self):
        #self.get_class(sqlite_setup)

    #def test_get_class_postgres(self):
        #self.get_class(postgres_setup)

    #def test_get_class_schema(self):
        #self.get_class(postgres_setup, schema='local')


# get_column
class TestGetColumn(unittest.TestCase):
    def get_column(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        result = get_column(table, 'id')
        self.assertEqual(result.name, 'id')
        self.assertEqual(type(result), sa.Column)

    def test_get_column_sqlite(self):
        self.get_column(sqlite_setup)

    def test_get_column_postgres(self):
        self.get_column(postgres_setup)

    def test_get_column_postgres(self):
        self.get_column(postgres_setup, schema='local')


class TestSelectRecords(unittest.TestCase):
    def select_records(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 2, 'name': 'Liam', 'age': 18, 'address_id': 1},
            {'id': 3, 'name': 'Emma', 'age': 19, 'address_id': 2},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2},
        ]
        results = select_records(table, engine, schema=schema, sorted=True)
        self.assertEqual(results, expected)

    def test_select_records_sqlite(self):
        self.select_records(sqlite_setup)

    def test_select_records_postgres(self):
        self.select_records(postgres_setup)

    def test_select_records_postgres(self):
        self.select_records(postgres_setup, schema='local')