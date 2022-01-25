"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import os
from typing import Dict, Optional, Union, Type

import numpy as np
import pandas as pd
import sqlite3 as sql
from contextlib import contextmanager
import datetime

import xpressinsight.types as xi_types
from xpressinsight.table_connector import TableConnector

SQLITE_FILENAME = "sqlite_connector.sqlite"

EXPORT_TYPE_MAP: Dict[Type[xi_types.BasicType], str] = {
    xi_types.boolean: 'BOOLEAN',
    xi_types.integer: 'INT',
    xi_types.string: 'TEXT',
    xi_types.real: 'FLOAT',
}


class Sqlite3Connector(TableConnector):
    def __init__(self, app, sqlite_file: str):
        super().__init__(app)
        self._sqlite_file: str = sqlite_file
        self._conn: Optional[sql.Connection] = None

    def _get_export_type(self, src_type: Type[xi_types.BasicType]) -> str:
        return EXPORT_TYPE_MAP[src_type]

    def _encode_column_name(self, ident: str) -> str:
        return self._encode_identifier(ident)

    def _decode_column_name(self, ident: str) -> str:
        (x, _, _) = ident.rpartition("_")
        return x

    def _clean_db(self):
        """Function which creates directory structure for the SQLite database
        (if it does not exist. If there is an existing database already present, it is deleted."""

        #
        os.makedirs(os.path.dirname(self._sqlite_file), exist_ok=True)

        if os.path.isfile(self._sqlite_file):
            os.remove(self._sqlite_file)

    def _does_db_exist(self):
        """Returns True iff database file exists"""
        return os.path.isfile(self._sqlite_file)

    def _check_db_exists(self):
        """Checks if the SQLite database files exists, if it does not, raises and exception"""

        if not self._does_db_exist():
            raise FileNotFoundError("Cannot find database {}".format(self._sqlite_file))

    def _has_table(self, table_name: str):
        #
        cur = self._conn.execute('SELECT name FROM sqlite_master WHERE type="table" and name=?', [table_name])
        num_tables = len(cur.fetchall())
        cur.close()
        return num_tables > 0

    def _get_table_info(self, table_name: str) -> pd.DataFrame:
        return pd.read_sql_query(f'PRAGMA table_info("{xi_types.validate_raw_ident(table_name)}")', self._conn)

    def _import_table(self, table_name: str) -> pd.DataFrame:
        start_time = datetime.datetime.utcnow()

        #
        select_table = f'SELECT * FROM "{xi_types.validate_raw_ident(table_name)}"'
        table = pd.read_sql_query(select_table, self._conn)
        table_info = self._get_table_info(table_name)

        for _, row in table_info.iterrows():
            col_dtype = row['type'].upper()

            if col_dtype == EXPORT_TYPE_MAP[xi_types.boolean]:
                #
                col_name = row['name']
                table[col_name] = table[col_name].astype(np.bool_, copy=False)
            if table.size == 0:
                #
                if col_dtype == EXPORT_TYPE_MAP[xi_types.integer]:
                    col_name = row['name']
                    table[col_name] = table[col_name].astype(np.int64, copy=False)
                elif col_dtype == EXPORT_TYPE_MAP[xi_types.real]:
                    col_name = row['name']
                    table[col_name] = table[col_name].astype(np.float64, copy=False)
                #
                #

        if self._verbose:
            end_time = datetime.datetime.utcnow()
            print('Imported {}: {}'.format(table_name, end_time - start_time))

        return table

    def _export_table(self, df: Union[pd.DataFrame, pd.Series], table_name: str, dtype: Dict[str, str],
                      index: bool = True, data_col_nullable: bool = False):
        start_time = datetime.datetime.utcnow()

        self._conn.execute(f'DROP TABLE IF EXISTS "{xi_types.validate_raw_ident(table_name)}"')
        table_columns = ', '.join(
            (f'"{xi_types.validate_raw_ident(idx_name)}" {xi_types.validate_raw_ident(idx_dtype)}'
             for idx_name, idx_dtype in dtype.items()))
        self._conn.execute(f'CREATE TABLE "{table_name}" ({table_columns})')

        df.to_sql(table_name, self._conn, if_exists="append", dtype=dtype, index=index)

        if self._verbose:
            end_time = datetime.datetime.utcnow()
            print('Exported {}: {}'.format(table_name, end_time - start_time))

    @contextmanager
    def _connect(self):
        """ Connect to a DB and disconnect when finished. """
        self._conn = sql.connect(self._sqlite_file)
        try:
            yield self._conn
        finally:
            self._conn.close()


class SQLiteConnector(Sqlite3Connector):
    def __init__(self, app):
        super().__init__(app, os.path.join(app.insight.work_dir, SQLITE_FILENAME))
