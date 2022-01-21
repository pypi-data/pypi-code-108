import unittest

from sqlalchemy.orm import Session

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.exceptions import ForceFail
from sessionize.utils.insert import insert_records_session


# insert_df_session
class TestInsertRecords(unittest.TestCase):

    def insert_records(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)

        new_people = [
            {'name': 'Odos', 'age': 35, 'address_id': 2},
            {'name': 'Kayla', 'age': 28, 'address_id': 2},
        ]
        
        with Session(engine) as session, session.begin():
            insert_records_session(table, new_people, session, schema=schema)

        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 2, 'name': 'Liam', 'age': 18, 'address_id': 1},
            {'id': 3, 'name': 'Emma', 'age': 19, 'address_id': 2},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2},
            {'id': 5, 'name': 'Odos', 'age': 35, 'address_id': 2},
            {'id': 6, 'name': 'Kayla', 'age': 28, 'address_id': 2}
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_insert_records_sqlite(self):
        self.insert_records(sqlite_setup)

    def test_insert_records_postgres(self):
        self.insert_records(postgres_setup)

    def test_insert_records_schema(self):
        self.insert_records(postgres_setup, schema='local')

    def insert_records_session_fails(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)

        new_people = [
            {'name': 'Odos', 'age': 35, 'addres_id': 2},
            {'name': 'Kayla', 'age': 28, 'addres_id': 2},
        ]
        
        try:
            with Session(engine) as session, session.begin():
                insert_records_session(table, new_people, session, schema=schema)
                raise ForceFail
        except ForceFail:
            pass

        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 2, 'name': 'Liam', 'age': 18, 'address_id': 1},
            {'id': 3, 'name': 'Emma', 'age': 19, 'address_id': 2},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2},
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_insert_records_session_fails_sqlite(self):
        self.insert_records_session_fails(sqlite_setup)
    
    def test_insert_records_session_fails_postgres(self):
        self.insert_records_session_fails(postgres_setup)

    def test_insert_records_session_fails_schema(self):
        self.insert_records_session_fails(postgres_setup, schema='local')
    