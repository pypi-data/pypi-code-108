#!/usr/bin/env python

"""Tests for `sql_query_tools` package."""


import unittest
from os import getpid
from sql_query_tools import Postgres
from sql_query_tools.utils import find_binary


class TestSQLQueryTools(unittest.TestCase):
    """
    Tests for `sql_query_tools` package.
    """
    def test_Postgres(self):
        try:
            pg = Postgres()
            connected = True
        except:
            connected = False

        if connected:
            # Not all users of this library will have Postgres set up, so only execute
            # tests if Postgres connected successfully.
            #
            # Now perform a series of commands to ensure that Postgres class methods are
            # working as intended.

            # Method: read_sql(). Choose a default table that always exists
            result = pg.read_sql('select * from information_schema.tables limit 1')

            # Method: get_table_name()
            self.assertEqual(pg.get_table_name(schema_name=None, table_name='pg_stat'), 'pg_stat')
            self.assertEqual(pg.get_table_name(schema_name='information_schema', table_name='tables'), 'information_schema.tables')

            # Method: validate_dtype()
            result = pg.validate_dtype(schema_name='information_schema',
                                       table_name='tables',
                                       col='table_catalog',
                                       val='string value')
            self.assertEqual(result, True)
            result = pg.validate_dtype(schema_name='information_schema',
                                       table_name='tables',
                                       col='table_catalog',
                                       val=5)
            self.assertEqual(result, False)

            # Method: infoschema()
            result = sorted(pg.infoschema(infoschema_table='tables').columns)
            result_sql_direct = sorted(pg.read_sql('select * from information_schema.tables limit 1').columns)
            self.assertEqual(result, result_sql_direct)

            # Method: build_update()
            result = pg.build_update(schema_name='pg_catalog',
                                     table_name='pg_stat_database',
                                     pkey_name='datid',
                                     pkey_value=12345,
                                     columns=['tup_returned', 'tup_fetched'],
                                     values=[11111, 22222],
                                     validate=True,
                                     newlines=False)
            expectation = 'UPDATE pg_catalog.pg_stat_database SET "tup_returned"=11111, "tup_fetched"=22222 WHERE "datid" = 12345'
            self.assertEqual(result, expectation)
            result = pg.build_update(schema_name='pg_catalog',
                                     table_name='pg_stat_database',
                                     pkey_name='datid',
                                     pkey_value=12345,
                                     columns=['tup_returned', 'tup_fetched'],
                                     values=[11111, 22222],
                                     validate=False,
                                     newlines=True)
            expectation = 'UPDATE pg_catalog.pg_stat_database\nSET "tup_returned"=11111, \n    "tup_fetched"=22222\nWHERE "datid" = 12345'
            self.assertEqual(result, expectation)

            # Method: build_insert()
            result = pg.build_insert(schema_name='pg_catalog',
                                     table_name='pg_stat_database',
                                     columns=['tup_returned', 'tup_fetched'],
                                     values=[11111, 22222],
                                     validate=True,
                                     newlines=False)
            expectation = 'insert into pg_catalog.pg_stat_database ("tup_returned", "tup_fetched") values (11111, 22222)'
            self.assertEqual(result, expectation)
            result = pg.build_insert(schema_name='pg_catalog',
                                     table_name='pg_stat_database',
                                     columns=['tup_returned', 'tup_fetched'],
                                     values=[11111, 22222],
                                     validate=False,
                                     newlines=True)
            expectation = 'insert into pg_catalog.pg_stat_database ("tup_returned", "tup_fetched")\nvalues (11111, 22222)'
            self.assertEqual(result, expectation)

            # Method: build_delete()
            result = pg.build_delete(schema_name='pg_catalog',
                                     table_name='pg_stat_database',
                                     pkey_name='datid',
                                     pkey_value=12345,
                                     newlines=False)
            expectation = 'delete from pg_catalog.pg_stat_database where datid = 12345'
            self.assertEqual(result, expectation)
            result = pg.build_delete(schema_name='pg_catalog',
                                     table_name='pg_stat_database',
                                     pkey_name='datid',
                                     pkey_value=12345,
                                     newlines=True)
            expectation = 'delete from pg_catalog.pg_stat_database\nwhere datid = 12345'
            self.assertEqual(result, expectation)

            # Method: col_names()
            result = pg.col_names(schema_name='pg_catalog', table_name='pg_stat_database')
            self.assertIn('datid', result)

            # Method: col_dtypes()
            result = pg.col_dtypes(schema_name='pg_catalog', table_name='pg_stat_database')
            self.assertEqual(result['datid'], 'oid')

            # Method: read_table()
            result = pg.read_table(schema_name='pg_catalog', table_name='pg_stat_database')
            self.assertGreater(result.shape[0], 0)
            self.assertGreater(result.shape[1], 0)

            # Method: dump()
            # Just make sure pg_dump is installed
            find_binary('pg_dump', abort=True)

            #
            # All create*, drop* and list* methods
            #

            pid = getpid()
            test_schema_name = f'test_schema_{pid}'
            test_table_name = f'test_table_{pid}'
            test_view_name = f'test_view_{pid}'

            pg.create_schema(schema_name=test_schema_name)

            try:
                # If any of the following fail, delete the test schema and raise error
                columnspec = {'col1': 'int', 'col2': 'text'}
                pg.create_table(schema_name=test_schema_name,
                                table_name=test_table_name,
                                columnspec=columnspec,
                                if_not_exists=False)

                result = pg.table_exists(schema_name=test_schema_name, table_name=test_table_name)
                self.assertTrue(result)

                pg.create_table(schema_name=test_schema_name,
                                table_name=test_table_name,
                                columnspec=columnspec,
                                if_not_exists=True)

                insert_fake_data_sql = pg.build_insert(schema_name=test_schema_name,
                                                    table_name=test_table_name,
                                                    columns=[k for k, v in columnspec.items()],
                                                    values=[5, 'test'],
                                                    validate=False,
                                                    newlines=False)

                pg.execute(insert_fake_data_sql)

                pg.create_view(schema_name=test_schema_name,
                            view_name=test_view_name,
                            view_sql=f'select * from {test_schema_name}.{test_table_name}',
                            or_replace=False)

                result = pg.view_exists(schema_name=test_schema_name, view_name=test_view_name)
                self.assertTrue(result)

                pg.create_view(schema_name=test_schema_name,
                            view_name=test_view_name,
                            view_sql=f'select * from {test_schema_name}.{test_table_name}',
                            or_replace=True)

                result = pg.read_table(schema_name=test_schema_name, table_name=test_view_name)
                self.assertEqual(result.to_dict(), {'col1': {0: 5}, 'col2': {0: 'test'}})

                pg.drop_view(schema_name=test_schema_name, view_name=test_view_name)
                pg.drop_table(schema_name=test_schema_name, table_name=test_table_name)
                pg.drop_schema(schema_name=test_schema_name)

            except Exception:
                pg.drop_schema(schema_name=test_schema_name)
                raise Exception

            # Method: _single_quote()
            self.assertEqual(pg._single_quote(5), 5)
            self.assertEqual(pg._single_quote('test'), "'test'")
            self.assertEqual(pg._single_quote("test's"), "'test''s'")

        else:
            raise Exception("Unable to establish Postgres connection, so no tests were run!")


case = TestSQLQueryTools()

test_methods = [x for x in dir(case) if x.startswith('test_')]
for method in test_methods:
    getattr(case, method)()