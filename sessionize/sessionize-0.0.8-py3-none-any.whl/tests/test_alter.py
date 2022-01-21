import unittest

from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy import VARCHAR, inspect

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.utils.sa_orm import get_table, get_column
from sessionize.exceptions import ForceFail
from sessionize.utils.alter import rename_column, drop_column, add_column, rename_table
from sessionize.utils.alter import copy_table, replace_primary_key, name_primary_key


# rename_column
class TestRenameColumn(unittest.TestCase):
    def rename_column(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        rename_column(table.name, 'name', 'first_name', engine, schema=schema)
        table = get_table(table.name, engine, schema=schema)
        cols = set(table.columns.keys())
        self.assertSetEqual(cols, {'id', 'age', 'first_name', 'address_id'})

    def test_rename_column_sqlite(self):
        self.rename_column(sqlite_setup)

    def test_rename_column_postgres(self):
        self.rename_column(postgres_setup)

    def test_rename_column_schema(self):
        self.rename_column(postgres_setup, schema='local')

    def raise_key_error(self, setup_function, error, schema=None):
        engine, table = setup_function(schema=schema)
        with self.assertRaises(error):
            rename_column(table.name, 'names', 'first_name', engine, schema=schema)

    def test_rename_column_key_error_sqlite(self):
        self.raise_key_error(sqlite_setup, KeyError)

    def test_rename_column_key_error_postgres(self):
        self.raise_key_error(postgres_setup, ProgrammingError)

    def test_rename_column_key_error_schema(self):
        self.raise_key_error(postgres_setup, ProgrammingError, schema='local')

    def raise_operational_error(self, setup_function, error, schema=None):
        engine, table = setup_function(schema=schema)
        with self.assertRaises(error):
            rename_column(table.name, 'name', 'age', engine, schema=schema)

    def test_rename_column_op_error_sqlite(self):
        self.raise_operational_error(sqlite_setup, OperationalError)

    def test_rename_column_op_error_postgres(self):
        self.raise_operational_error(postgres_setup, ProgrammingError)

    def test_rename_column_op_error_schema(self):
        self.raise_operational_error(postgres_setup, ProgrammingError, schema='local')

# drop_column
class TestDropColumn(unittest.TestCase):
    def drop_column(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        drop_column(table.name, 'name', engine, schema=schema)
        table = get_table(table.name, engine, schema=schema)
        cols = set(table.columns.keys())
        self.assertSetEqual(cols, {'id', 'age', 'address_id'})

    def test_drop_column_sqlite(self):
        self.drop_column(sqlite_setup)

    def test_drop_column_postgres(self):
        self.drop_column(postgres_setup)
    
    def test_drop_column_schema(self):
        self.drop_column(postgres_setup, schema='local')

    def raise_key_error(self, setup_function, error, schema=None):
        engine, table = setup_function(schema=schema)
        with self.assertRaises(error):
            drop_column(table.name, 'names', engine, schema=schema)

    def test_drop_column_key_error_sqlite(self):
        self.raise_key_error(sqlite_setup, KeyError)

    def test_drop_column_key_error_postgres(self):
        self.raise_key_error(postgres_setup, ProgrammingError)

    def test_drop_column_key_error_schema(self):
        self.raise_key_error(postgres_setup, ProgrammingError, schema='local')
    

# add_column
class TestAddColumn(unittest.TestCase):
    def add_column(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        table = add_column(table.name, 'last_name', str, engine, schema=schema)
        cols = set(table.columns.keys())
        self.assertSetEqual(cols, {'id', 'age', 'name', 'address_id', 'last_name'})
        self.assertIs(VARCHAR, type(get_column(table, 'last_name').type))

    def test_add_column_sqlite(self):
        self.add_column(sqlite_setup)

    def test_add_column_postgres(self):
        self.add_column(postgres_setup)

    def test_add_column_schema(self):
        self.add_column(postgres_setup, schema='local')

    def raise_operational_error(self, setup_function, error, schema=None):
        engine, table = setup_function(schema=schema)
        with self.assertRaises(error):
            add_column(table.name, 'name', str, engine, schema=schema)

    def test_add_column_op_error_sqlite(self):
        self.raise_operational_error(sqlite_setup, OperationalError)

    def test_add_column_op_error_postgres(self):
        self.raise_operational_error(postgres_setup, ProgrammingError)

    def test_add_column_op_error_schema(self):
        self.raise_operational_error(postgres_setup, ProgrammingError, schema='local')


class TestRenameTable(unittest.TestCase):
    def rename_table(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        new_table_name = 'employees'
        table_names = inspect(engine).get_table_names(schema=schema)
        table_names.remove(table.name)
        table = rename_table(table.name, new_table_name, engine, schema=schema)
        table_names.append(new_table_name)
        new_table_names = inspect(engine).get_table_names(schema=schema)
        self.assertSetEqual(set(table_names), set(new_table_names))

    def test_rename_table_sqlite(self):
        self.rename_table(sqlite_setup)

    def test_rename_table_postgres(self):
        self.rename_table(postgres_setup)

    def test_rename_table_schema(self):
        self.rename_table(postgres_setup, schema='local')

    def raise_key_error(self, setup_function, error, schema=None):
        engine, table = setup_function(schema=schema)
        new_table_name = 'places'
        with self.assertRaises(error):
            rename_table(table.name, new_table_name, engine, schema=schema)

    def test_rename_table_fail_sqlite(self):
        self.raise_key_error(sqlite_setup, OperationalError)

    def test_rename_table_fail_postgres(self):
        self.raise_key_error(postgres_setup, ProgrammingError)

    def test_rename_table_fail_schema(self):
        self.raise_key_error(postgres_setup, ProgrammingError, schema='local')


# TODO: copy_table tests
class TestCopyTable(unittest.TestCase):
    def copy_table(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        new_table_name = 'employees'
        table_names = inspect(engine).get_table_names(schema=schema)
        copy_table(table.name, new_table_name, engine, schema=schema)
        table_names.append(new_table_name)
        new_table_names = inspect(engine).get_table_names(schema=schema)
        self.assertSetEqual(set(table_names), set(new_table_names))

    def test_copy_table_sqlite(self):
        self.copy_table(sqlite_setup)

    def test_copy_table_postgres(self):
        self.copy_table(postgres_setup)

    def test_copy_table_schema(self):
        self.copy_table(postgres_setup, schema='local')
 

# TODO: replace_primary_key tests
class TestReplacePrimaryKey(unittest.TestCase):
    pass

# TODO: create_primary_key tests - Only use on a table with no primary key.
class TestCreatePrimaryKey(unittest.TestCase):
    pass

# TODO: name_primary_key tests
class TestNamePrimaryKey(unittest.TestCase):
    pass