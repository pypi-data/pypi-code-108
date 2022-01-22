#!/usr/bin/env python
"""
Module MYSQL -- MySQL Database Interface
Sub-Package DBTOOLS of Package PLIB
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements the MySQL interface built with
PLIB.DBTOOLS.
"""

import MySQLdb

from plib.dbtools import DBInterface


class MySQLDBInterface(DBInterface):
    
    db_mod = MySQLdb
    
    def _get_connection(self, *args, **kwargs):
        return MySQLdb.connect(**kwargs)
    
    def _get_fieldspec(self, field):
        # Fieldspecs are already in MySQL format
        return field
    
    tables_sql = "SHOW TABLES;"
    tables_index = 0
    
    fields_sql = "SHOW FIELDS IN {0};"
    fields_iter = True
    
    index_sql = "SHOW INDEXES IN {0};"
    
    use_unicode = True
    
    def _get_fieldvalue(self, row):
        # TODO: add field type and canonicalize
        return row[0]  # type is row[1] in datatype(bytes) format
    
    def _table_sql(self, tablename, fieldspecs):
        return "CREATE TABLE {0}({1});".format(
            tablename,
            fieldspecs
        )
    
    def _index_sql(self, tablename, column_str, primary=False):
        return "ALTER TABLE {0} ADD {1} ({2});".format(
            tablename,
            "PRIMARY KEY" if primary else "INDEX",
            column_str
        )
