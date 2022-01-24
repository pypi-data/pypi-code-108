#!/usr/bin/python
#
#    Copyright 2020, phData, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import sys
import re
from pathlib import Path

# cx_Oracle is a heavyweight package so we should not require it
CX_ORACLE_IMPORT_SUCCESS = True
try:
    import cx_Oracle
except Exception as e:
    sys.stderr.write("WARNING: Unable to import cx_Oracle: {}\n".format(e))
    CX_ORACLE_IMPORT_SUCCESS = False

# Represents a database connection url
class DbURL(object):
    def __init__(self, user, password, host, port, service):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.service = service

    def __repr__(self):
        return "{}/XXXXXX@//{}:{}/{}".format(self.user, self.host, self.port, self.service)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

# easy to access map, should replace with a real object where used
class Struct(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    def __str__(self):
        return str(self.__dict__)

# NOTE: as we add more supported objects we need to add new regexes to SPLIT_OBJECT_REGEXES

GET_ALL_TABLES_SQL = """
SELECT OWNER, TABLE_NAME, DBMS_METADATA.GET_DDL('TABLE', TABLE_NAME, OWNER)
FROM ALL_TABLES WHERE OWNER LIKE '{schema}' AND TABLE_NAME LIKE '{table}'
"""

GET_ALL_VIEWS_SQL = """
SELECT OWNER, VIEW_NAME, DBMS_METADATA.GET_DDL('VIEW', VIEW_NAME, OWNER)
FROM ALL_VIEWS WHERE OWNER LIKE '{schema}' AND VIEW_NAME LIKE '{view}'
"""

GET_SECONDARY_INDEXES_SQL = """
SELECT DBMS_METADATA.GET_DEPENDENT_DDL('INDEX',TABLE_NAME, TABLE_OWNER) FROM (
    SELECT table_name, table_owner, INDEX_NAME FROM all_indexes
    WHERE table_owner = '{schema}' AND table_name = '{table}'
    AND index_name NOT IN (
        SELECT constraint_name FROM sys.all_constraints
        WHERE table_name = table_name AND constraint_type = 'P'
    ) AND ROWNUM = 1
)
"""

GET_PRIMARY_KEYS_SQL = """
SELECT DBMS_METADATA.GET_DDL('CONSTRAINT', CONSTRAINT_NAME, OWNER)
FROM ALL_CONSTRAINTS c WHERE CONSTRAINT_TYPE = 'P' AND INDEX_OWNER = '{schema}' AND TABLE_NAME = '{table}'
"""

GET_COMMENTS_SQL = """
SELECT DBMS_METADATA.GET_DEPENDENT_DDL('COMMENT', TABLE_NAME, OWNER)
FROM ALL_TABLES WHERE OWNER = '{schema}' AND TABLE_NAME = '{table}'
"""

GET_VIEW_COMMENTS_SQL = """
SELECT DBMS_METADATA.GET_DEPENDENT_DDL('COMMENT', VIEW_NAME, OWNER)
FROM ALL_VIEWS WHERE OWNER = '{schema}' AND VIEW_NAME = '{view}'
"""

# Parse oracles strange syntax better, see tests for examples
SPLIT_OBJECT_REGEXES = [
  "ALTER\s+TABLE",
  "ALTER\s+VIEW",
  "COMMENT\s+ON",
  "CREATE\s+(UNIQUE\s+)?INDEX",
  "CREATE\s+TABLE",
  "CREATE\s+VIEW"
]

# Responsible for crawling the oracle schema
class OracleSchemaCrawler(object):
    def __init__(self, host, port, service, user, password):
        self.dsn = cx_Oracle.makedsn(
            host,
            port,
            service_name=service
        )
        self.conn = cx_Oracle.connect(
            user=user,
            password=password,
            dsn=self.dsn
        )
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()

    def __exec(self, sql):
        sys.stderr.write("EXECUTING: %s\n" % sql)
        self.c.execute(sql)
        rows = []
        try:
          for row in self.c:
              rows.append(row)
        except Exception as e:
          s = str(e)
          # Should be only
          # cx_Oracle.DatabaseError: ORA-31608: specified object of type COMMENT not found
          # but oracle codes are reliable
          if re.search("specified object of type [A-z]+ not found", s):
              sys.stderr.write("Ignoring %s\n" % (s))
              pass
          else:
              raise e
        return rows

    def __populate_dependent_ddl(self, table):
        # INDEXES
        for row in self.__exec(GET_SECONDARY_INDEXES_SQL.format(schema=table.schema, table=table.name)):
            table.post_ddl += _oracle_split_manually(row[0].read())
        # PRIMARY KEYS
        for row in self.__exec(GET_PRIMARY_KEYS_SQL.format(schema=table.schema, table=table.name)):
            table.post_ddl += _oracle_split_manually(row[0].read())
        # COMMENTS
        for row in self.__exec(GET_COMMENTS_SQL.format(schema=table.schema, table=table.name)):
            table.post_ddl += _oracle_split_manually(row[0].read())

    def __populate_view_dependent_ddl(self, view):
        # COMMENTS
        for row in self.__exec(GET_VIEW_COMMENTS_SQL.format(schema=view.schema, view=view.name)):
            view.post_ddl += _oracle_split_manually(row[0].read())


    def collect_ddl(self, schema_pattern, table_pattern, view_pattern, outputPath):
        tables = []
        views = []
        results = []
        outputPath.mkdir(parents=True, exist_ok=True)
        if table_pattern is not None:
            for row in self.__exec(GET_ALL_TABLES_SQL.format(schema=schema_pattern, table=table_pattern)):
                table_ddl = _oracle_split_manually(row[2].read())
                tables.append(Struct(schema=row[0], name=row[1], object_type='TABLE', table_ddl=table_ddl, pre_ddl=[], post_ddl=[]))
            for table in tables:
                self.__populate_dependent_ddl(table)
        if view_pattern is not None:
            for row in self.__exec(GET_ALL_VIEWS_SQL.format(schema=schema_pattern, view=view_pattern)):
                view_ddl = _oracle_split_manually(row[2].read())
                views.append(Struct(schema=row[0], name=row[1], object_type='VIEW', table_ddl=view_ddl, pre_ddl=[], post_ddl=[]))
            for view in views:
                self.__populate_view_dependent_ddl(view)
        for table in tables + views:
            outputFile = outputPath.joinpath("{}-AND-DEPENDENTS-{}-{}.sql".format(table.object_type, table.schema, table.name).upper())
            with outputFile.open('w') as fh:
                for ddl in table.pre_ddl:
                    fh.write(ddl)
                    fh.write(";\n")
                for ddl in table.table_ddl:
                    fh.write(ddl)
                    fh.write(";\n")
                for ddl in table.post_ddl:
                    fh.write(ddl)
                    fh.write(";\n")
            results.append(outputFile)
        return results

# Parses Oracle's EZConnect syntax
def _oracle_parse_url(url):
    m = re.match("^([^/]+)/([^@]+)@(/{2})?([^:/]+)(:[^/]+)?/(.*)", url)
    if m and len(m.groups()) == 6:
        user = m.group(1)
        password = m.group(2)
        host = m.group(4)
        port = m.group(5)
        if not port: port = '1521'
        if port[0] == ':': port = port[1:]
        service = m.group(6)
        return DbURL(user, password, host, port, service)
    else:
        raise Exception("Invalid db url %s, expected format USER/PASSWORD@//hostname:port/service_name" % (url))

def __regex_match_any(regexes, line):
    for regex in regexes:
        if re.search(regex, line, re.IGNORECASE): return True
    return False

def _oracle_split_lob_by_regex(regexes, sql):
    buff = []
    result = []
    for line in sql.replace('\r','\n').split("\n"):
        if not line: continue
        if not buff:
            buff.append(line)
        elif __regex_match_any(regexes, line):
            result.append("\n".join(buff))
            buff = []
            buff.append(line)
        else:
            buff.append(line)
    result.append("\n".join(buff))
    return [i for i in result if i.strip() ]

def _oracle_split_manually(sql):
    return _oracle_split_lob_by_regex(SPLIT_OBJECT_REGEXES, sql)

def oracle_collect_sql(url, schema, table, view, outputPath):
    url = _oracle_parse_url(url)
    sys.stderr.write("Connecting to: %s\n" % (url))
    sc = OracleSchemaCrawler(url.host, url.port, url.service, url.user, url.password)
    sc.collect_ddl(schema, table, view,outputPath)
    sc.close()

