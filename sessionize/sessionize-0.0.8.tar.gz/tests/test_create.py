import unittest

from sqlalchemy import inspect, Table, INTEGER, VARCHAR
from sqlalchemy.exc import OperationalError, ProgrammingError

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.create import create_table
from sessionize.utils.sa_orm import get_column_types, get_primary_key_constraints


class TestCreateTable(unittest.TestCase):
    def create_table(self, setup_function, schema=None):
        engine, _ = setup_function(schema=schema)

        cols = ['id', 'name', 'age']
        types = [int, str, int]
        new_table = create_table('test_people', cols, types, 'id', engine, schema)

        table_names = inspect(engine).get_table_names(schema=schema)
        col_types = get_column_types(new_table)
        expected = {'id': INTEGER(), 'name': VARCHAR(), 'age': INTEGER()}
        _, keys = get_primary_key_constraints(new_table)

        self.assertIn('test_people', table_names)
        self.assertIs(type(new_table), Table)
        self.assertIs(type(col_types['id']), type(expected['id']))
        self.assertIs(type(col_types['name']), type(expected['name']))
        self.assertIs(type(col_types['age']), type(expected['age']))
        self.assertListEqual(keys, ['id'])


    def test_create_table_sqlite(self):
        self.create_table(sqlite_setup)

    def test_create_table_postgres(self):
        self.create_table(postgres_setup)

    def test_create_table_schema(self):
        self.create_table(postgres_setup, schema='local')

    def create_table_error(self, setup_function, error, schema=None):
        engine, table = setup_function(schema=schema)

        cols = ['id', 'name', 'age']
        types = [int, str, int]
        with self.assertRaises(error):
            create_table(table.name, cols, types, 'id', engine, schema, if_exists='error')

    def test_create_table_error_sqlite(self):
        self.create_table_error(sqlite_setup, OperationalError)

    def test_create_table_error_postgres(self):
        self.create_table_error(postgres_setup, ProgrammingError)

    def test_create_table_error_schema(self):
        self.create_table_error(postgres_setup, ProgrammingError, schema='local')

