import unittest

from sqlalchemy.orm import Session
from sqlalchemy import inspect, Table
from sqlalchemy.exc import OperationalError, ProgrammingError

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.exceptions import ForceFail
from sessionize.utils.create import create_table


# create_table
class TestCreateTable(unittest.TestCase):
    def create_table(self, setup_function, schema=None):
        engine, _ = setup_function(schema=schema)

        cols = ['id', 'name', 'age']
        types = [int, str, int]
        table = create_table('test_people', cols, types, 'id', engine, schema)

        table_names = inspect(engine).get_table_names(schema=schema)
        self.assertIn('test_people', table_names)
        self.assertIs(type(table), Table)

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

