#!/usr/bin/env python3
"""
TEST.DBTOOLS.TEST_DBTOOLS.PY -- test script for state machine class
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the PLIB.DBTOOLS DB interface classes.
"""

import os
import tempfile
import unittest

from plib.dbtools import get_db_interface, DB_MYSQL, DB_SQLITE3


TEST_DB_STRUCTURE = {
    "tables": {
        "test_table_1": (
            "test_field_1_s varchar(10)",
            "test_field_1_i int",
            "test_field_1_b bool",
        ),
        "test_table_2": (
            "test_field_2_i int",
            "test_field_2_s varchar(10)",
            "test_field_2_b bool",
        ),
    },
    "keys": {
        "test_table_1": "test_field_1_s",
        "test_table_2": "test_field_2_i",
    },
    "indexes": {
        "test_table_1": (
            "test_field_1_i",
        ),
        "test_table_2": (
            "test_field_2_s",
        ),
    },
}

TEST_TABLES = list(TEST_DB_STRUCTURE["tables"].keys())


class DBToolsTest(object):
    
    dbname = "plib_test"  # can be overridden if tester cannot provide a DB with this name
    dbtype = None
    structure = TEST_DB_STRUCTURE
    params = None
    argpath = None
    kwds = None
    
    def get_test_intf(self):
        return get_db_interface(
            self.dbname,
            self.dbtype,
            self.structure,
            self.params,
            self.argpath,
            self.kwds
        )
    
    def test_dbtools(self):
        intf = self.get_test_intf()
        try:
            self.assertEqual(intf.get_tables(), [])
            
            intf.create_tables()
            intf.create_keys()
            intf.create_indexes()
            
            self.assertEqual(intf.get_tables(), TEST_TABLES)
            
            intf.clear_tables()
        finally:
            intf.close()


class SQLite3Test(DBToolsTest, unittest.TestCase):
    
    dbtype = DB_SQLITE3
    
    def setUp(self):
        # Set up db in temporary directory
        self.argpath = tempfile.mkdtemp()  # the DB file will be automatically created here
    
    def tearDown(self):
        # Delete db and temporary directory
        for f in os.listdir(self.argpath):
            os.remove(os.path.join(self.argpath, f))
        os.rmdir(self.argpath)
        self.argpath = None


class MySQLTest(DBToolsTest, unittest.TestCase):
    
    dbtype = DB_MYSQL
    
    cred_filename = os.path.expanduser(os.path.join("~", ".plib_test.json"))  # can be overridden if needed
    
    def setUp(self):
        # Must have externally reachable empty DB available
        from plib.stdlib.jsontools import load_json
        self.kwds = dict(db=self.dbname, **load_json(self.cred_filename))
    
    def tearDown(self):
        # The test clears all tables at the end, so the DB should be empty again
        self.kwds = None


if __name__ == '__main__':
    unittest.main()
