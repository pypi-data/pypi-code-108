import unittest

from sqlalchemy.orm import Session

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.exceptions import ForceFail
from sessionize.utils.insert import insert_records_session
from sessionize.utils.update import update_records_session
from sessionize.utils.delete import delete_records_session


# TODO: insert & update & delete
# TODO: insert & delete & fail
# TODO: insert & update & delete & fail


class TestCombined(unittest.TestCase):
    def insert_update(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)

        new_people = [
            {'name': 'Odos', 'age': 35, 'address_id': 2},
            {'name': 'Kayla', 'age': 28, 'address_id': 2}
        ]

        new_ages = [
            {'id': 2, 'name': 'Liam', 'age': 19},
            {'id': 3, 'name': 'Emma', 'age': 20}
        ]
        
        with Session(engine) as session, session.begin():
            insert_records_session(table, new_people, session, schema=schema)
            update_records_session(table, new_ages, session, schema=schema)

        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 2, 'name': 'Liam', 'age': 19, 'address_id': 1},
            {'id': 3, 'name': 'Emma', 'age': 20, 'address_id': 2},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2},
            {'id': 5, 'name': 'Odos', 'age': 35, 'address_id': 2},
            {'id': 6, 'name': 'Kayla', 'age': 28, 'address_id': 2}
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_insert_update_sqlite(self):
        self.insert_update(sqlite_setup)

    def test_insert_update_postgres(self):
        self.insert_update(postgres_setup)

    def test_insert_update_schema(self):
        self.insert_update(postgres_setup, schema='local')

    def delete_update_fail(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)

        new_ages = [
            {'id': 2, 'name': 'Liam', 'age': 19},
            {'id': 3, 'name': 'Emma', 'age': 20}
        ]

        try:
            with Session(engine) as session, session.begin():
                delete_records_session(table, 'id', [2, 3], session, schema=schema)
                update_records_session(table, new_ages, session, schema=schema)
        except:
            pass

        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 2, 'name': 'Liam', 'age': 18, 'address_id': 1},
            {'id': 3, 'name': 'Emma', 'age': 19, 'address_id': 2},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2},
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_delete_update_fail_sqlite(self):
        self.delete_update_fail(sqlite_setup)

    def test_delete_update_fail_postgres(self):
        self.delete_update_fail(postgres_setup)

    def test_delete_update_fail_schema(self):
        self.delete_update_fail(postgres_setup, schema='local')

    def update_delete(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)

        new_ages = [
            {'id': 2, 'name': 'Liam', 'age': 19},
            {'id': 3, 'name': 'Emma', 'age': 20}
        ]

        with Session(engine) as session, session.begin():
            update_records_session(table, new_ages, session, schema=schema)
            delete_records_session(table, 'id', [2, 3], session, schema=schema)
            
        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2},
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_update_delete_sqlite(self):
        self.update_delete(sqlite_setup)

    def test_update_delete_postgres(self):
        self.update_delete(postgres_setup)

    def test_update_delete_schema(self):
        self.update_delete(postgres_setup, schema='local')

    def delete_insert_update(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)

        new_people = [
            {'name': 'Odos', 'age': 35, 'address_id': 2},
            {'name': 'Kayla', 'age': 28, 'address_id': 2}
        ]

        new_ages = [
            {'id': 1, 'name': 'Olivia', 'age': 18},
            {'id': 4, 'name': 'Noah', 'age': 21}
        ]

        with Session(engine) as session, session.begin():
            delete_records_session(table, 'id', [2, 3], session, schema=schema)
            insert_records_session(table, new_people, session, schema=schema)
            update_records_session(table, new_ages, session, schema=schema)
            
        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 18, 'address_id': 1},
            {'id': 4, 'name': 'Noah', 'age': 21, 'address_id': 2},
            {'id': 5, 'name': 'Odos', 'age': 35, 'address_id': 2},
            {'id': 6, 'name': 'Kayla', 'age': 28, 'address_id': 2}
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_delete_insert_update_sqlite(self):
        self.delete_insert_update(sqlite_setup)

    def test_delete_insert_update_postgres(self):
        self.delete_insert_update(postgres_setup)

    def test_delete_insert_update_schema(self):
        self.delete_insert_update(postgres_setup, schema='local')
