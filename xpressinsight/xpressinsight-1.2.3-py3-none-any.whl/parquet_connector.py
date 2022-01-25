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
import pyarrow as pa
import pyarrow.parquet as pq
from contextlib import contextmanager
import datetime

import xpressinsight.types as xi_types
from xpressinsight.table_connector import TableConnector, SingleValueDict

PARQUET_DIR = "parquet"

EXPORT_TYPE_MAP: Dict[Type[xi_types.BasicType], pa.DataType] = {
    xi_types.boolean: pa.bool_(),
    xi_types.integer: pa.int32(),
    xi_types.string: pa.utf8(),
    xi_types.real: pa.float64(),
}


class ParquetConnector(TableConnector):
    def __init__(self, app, parquet_dir: Optional[str] = None):
        super().__init__(app)
        self._parquet_dir: str = os.path.join(app.insight.work_dir, PARQUET_DIR)\
            if parquet_dir is None else parquet_dir

    def _get_export_type(self, src_type: Type[xi_types.BasicType]) -> pa.DataType:
        return EXPORT_TYPE_MAP[src_type]

    def _encode_column_name(self, ident: str) -> str:
        return ident

    def _decode_column_name(self, ident: str) -> str:
        return ident

    def _clean_db(self):
        """ Creates directory structure for parquet data repository if it does not exist.
        If parquet folder contains parquet files, delete all of them. """
        #
        #
        try:
            os.makedirs(self._parquet_dir, exist_ok=True)
            files = os.listdir(self._parquet_dir)

            for file in files:
                if file.endswith(".parquet"):
                    os.remove(os.path.join(self._parquet_dir, file))
        except OSError as err:
            raise OSError(f'Could not clean data repository directory: "{self._parquet_dir}".\nOSError: {err}')

    def _does_db_exist(self):
        """Returns True iff data repository directory exists"""
        return os.path.isdir(self._parquet_dir)

    def _check_db_exists(self):
        """Checks if the SQLite database files exists, if it does not, raises and exception"""

        if not self._does_db_exist():
            raise FileNotFoundError(f'Cannot find data repository directory: "{self._parquet_dir}".')

    def _save_single_values_db(self, prefix: str, values: SingleValueDict):
        """Saves SingleValueDict to the database"""

        assert prefix in ("SCALAR", "PARAM", "META")

        for dtype in xi_types.ALL_BASIC_TYPE:
            #
            if dtype in values and values[dtype]:
                #
                #
                #
                #
                table_name = "{}_{}".format(prefix, dtype.__name__)
                schema = pa.schema([
                    pa.field('Name', pa.utf8(), False),
                    pa.field('Value', EXPORT_TYPE_MAP[dtype], False)
                ])
                #
                arrow_table = pa.Table.from_pydict({
                    'Name': values[dtype].keys(),
                    'Value': values[dtype].values()
                }, schema=schema)
                self._export_table(arrow_table, table_name, dtype={})
                del arrow_table

    def _get_pq_file_path(self, table_name):
        return os.path.join(self._parquet_dir, table_name + '.parquet')

    def _has_table(self, table_name: str):
        return os.path.isfile(self._get_pq_file_path(table_name))

    @staticmethod
    def _int64_conversion(table: pd.DataFrame, schema: pa.Schema):
        for field in schema:
            if pa.types.is_integer(field.type) and not pd.api.types.is_int64_dtype(table[field.name].dtype):
                table[field.name] = table[field.name].astype(np.int64, copy=False)

    def _import_table(self, table_name: str) -> pd.DataFrame:
        """Import parquet file as flat DataFrame with indices as normal columns."""
        #
        start_time = datetime.datetime.utcnow()

        #
        #
        arrow_table = pq.read_table(self._get_pq_file_path(table_name))
        #
        table = arrow_table.to_pandas(ignore_metadata=True)

        #
        #
        ParquetConnector._int64_conversion(table, arrow_table.schema)
        del arrow_table

        if self._verbose:
            end_time = datetime.datetime.utcnow()
            print('Imported {}: {}'.format(table_name, end_time - start_time))

        return table

    @staticmethod
    def _get_schema(df: pd.DataFrame, dtype: Dict[str, pa.DataType], data_col_nullable: bool):
        #
        return pa.schema(
            #
            #
            [pa.field(f_name, f_type, f_name not in df.index.names and data_col_nullable)
             for f_name, f_type in dtype.items()]
        )

    def _export_table(self, df: Union[pa.Table, pd.DataFrame, pd.Series], table_name: str,
                      dtype: Dict[str, pa.DataType], index: bool = True, data_col_nullable: bool = False):
        start_time = datetime.datetime.utcnow()

        #
        if isinstance(df, pd.Series):
            #
            df = df.to_frame()

        if isinstance(df, pd.DataFrame):
            #
            schema = self._get_schema(df, dtype, data_col_nullable)
            #
            arrow_table = pa.Table.from_pandas(df, schema=schema, preserve_index=index)
        elif isinstance(df, pa.Table):
            #
            arrow_table = df
        else:
            raise TypeError(f'Unexpected table type. Cannot export: {type(df)}.')

        #
        #
        pq.write_table(arrow_table, where=self._get_pq_file_path(table_name), compression='NONE')
        del arrow_table

        if self._verbose:
            end_time = datetime.datetime.utcnow()
            print('Exported {}: {}'.format(table_name, end_time - start_time))

    @contextmanager
    def _connect(self):
        """ Check if parquet directory exists. """
        self._check_db_exists()
        try:
            yield self._parquet_dir
        finally:
            pass
