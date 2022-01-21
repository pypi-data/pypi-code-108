import unittest

from sqlalchemy.orm import Session

from sessionize.utils.delete import delete_records_session
from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.exceptions import ForceFail


# delete_record_session
class TestDeleteRecords(unittest.TestCase):

    def delete_records(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        
        with Session(engine) as session, session.begin():
            delete_records_session(table, 'id', [2, 3], session, schema=schema)

        expected = [
            {'id': 1, 'name': 'Olivia', 'age': 17, 'address_id': 1},
            {'id': 4, 'name': 'Noah', 'age': 20, 'address_id': 2}
        ]

        results = select_records(table, engine, schema=schema, sorted=True)

        self.assertEqual(results, expected)

    def test_delete_records_sqlite(self):
        self.delete_records(sqlite_setup)

    def test_delete_records_postgres(self):
        self.delete_records(postgres_setup)

    def test_delete_records_schema(self):
        self.delete_records(postgres_setup, schema='local')

    def delete_records_session_fails(self, setup_function, schema=None):
        engine, table = setup_function(schema=schema)
        
        try:
            with Session(engine) as session, session.begin():
                delete_records_session(table, 'id', [1, 2], session, schema=schema)
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

    def test_delete_records_session_fails_sqlite(self):
        self.delete_records_session_fails(sqlite_setup)

    def test_delete_records_session_fails_postgres(self):
        self.delete_records_session_fails(postgres_setup)

    def test_delete_records_session_fails_schema(self):
        self.delete_records_session_fails(postgres_setup, schema='local')