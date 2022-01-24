# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for parquet based serialization and deserialization."""
import errno
import logging
import os.path
from typing import cast

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    DiskFull, InsufficientMemory)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ResourceException
from scipy import sparse

logger = logging.getLogger(__name__)


class Parqueter:
    """Default Parqueter based on Pandas implementation."""

    _compression = "gzip"

    @staticmethod
    def dump_numpy_array(obj: np.ndarray, path: str) -> str:
        """
        Dump a numpy array to a parquet file. This will convert a single dimensional object to
        two dimensions.

        :param obj: The numpy array to serialize.
        :param path: Path to dump the file to.
        :return: The path.
        """
        Contract.assert_type(
            value=obj, name="obj", expected_types=np.ndarray, log_safe=True
        )
        Contract.assert_value(value=path, name="path")
        num_rows = obj.shape[0]
        # Convert `obj` to 2-dimensions.
        if obj.ndim == 1:
            obj = obj.reshape(num_rows, 1)

        df_wrapper = pd.DataFrame(obj)
        return Parqueter.dump_pandas_dataframe(df_wrapper, path)

    @staticmethod
    def dump_pandas_dataframe(obj: pd.DataFrame, path: str) -> str:
        """
        Dump a pandas dataframe object to a parquet file. This will write a 2-dimensional
        array even if the input object is one-dimensional.

        :param obj: The pandas dataframe to serialize.
        :param path: Path to dump the file to.
        :return: The path.
        """
        Contract.assert_type(
            value=obj, name="obj", expected_types=pd.DataFrame, log_safe=True
        )
        Contract.assert_value(value=path, name="path")
        try:
            num_rows = obj.shape[0]
            # Convert `obj` to 2-dimensions.
            if obj.ndim == 1:
                obj = obj.reshape(num_rows, 1)

            df = pd.DataFrame(obj)
            # `to_parquet` only supports string column names.
            df.columns = [str(c) for c in df.columns]
            df.to_parquet(path, compression=Parqueter._compression)
        except MemoryError as me:
            raise ResourceException._with_error(
                AzureMLError.create(InsufficientMemory), inner_exception=me
            ) from me
        except OSError as oe:
            if oe.errno == errno.ENOSPC:
                raise ResourceException._with_error(
                    AzureMLError.create(
                        DiskFull,
                        target="pandas.DataFrame.to_parquet",
                        operation_name="pandas.DataFrame.to_parquet",
                    ),
                    inner_exception=oe,
                ) from oe
            else:
                logger.error(
                    "Failed to store as a parquet file to disk. OS Error Code: {}".format(
                        str(oe.errno)
                    )
                )
                raise
        except Exception as e:
            logging_utilities.log_traceback(e, None)
            raise

        return path

    @staticmethod
    def dump_sparse_matrix(obj: sparse.spmatrix, path: str) -> str:
        """
        Dump a scipy sparse matrix object to a parquet file.
        :param obj: Scipy sparse matrix to serialize.
        :param path: Path to dump the file to.
        :return: The path.
        """
        Contract.assert_type(
            value=obj, name="obj", expected_types=sparse.spmatrix, log_safe=True
        )
        Contract.assert_value(value=path, name="path")
        coo = obj.tocoo()
        try:
            df_wrapper = pd.DataFrame(
                {"row": coo.row, "col": coo.col, "data": coo.data}
            )

            pa_table = pa.Table.from_pandas(df_wrapper)
            custom_metadata = {
                "shape_x": str(coo.shape[0]),
                "shape_y": str(coo.shape[1]),
            }
            merged_metadata = {**custom_metadata, **(pa_table.schema.metadata or {})}
            updated_table = pa_table.replace_schema_metadata(merged_metadata)
            pq.write_table(updated_table, path)
        except Exception:
            logger.error("Failed to serialize sparse pandas dataframe into parquet.")
            raise

        return path

    @staticmethod
    def load_pandas_dataframe(path: str) -> pd.DataFrame:
        """
        Deserialize parquet file into a pandas dataframe.

        :param path: The file path used by the parqueter.
        :return: The deserialized pandas dataframe.
        """
        try:
            df = pd.read_parquet(path)
            logger.debug(
                "Deserialized parquet file into a pandas dataframe of shape: {}".format(
                    df.shape
                )
            )
            inmemory_size_kb = df.memory_usage(deep=True).sum() / 1e3
            ondisk_size_kb = os.path.getsize(path) / 1e3
            logger.info(
                f"parquet to ndarray. Memory: {inmemory_size_kb:.2f} kb,"
                f"Disk: {ondisk_size_kb:.2f} kb"
            )
            return df
        except MemoryError as me:
            raise ResourceException._with_error(
                AzureMLError.create(InsufficientMemory), inner_exception=me
            ) from me
        except Exception as e:
            if isinstance(e, OSError):
                logger.error(
                    "Failed to load the parquet file from disk. OS Error Code: {}".format(
                        str(e.errno)
                    )
                )
            logging_utilities.log_traceback(e, None)
            raise

    @staticmethod
    def load_numpy_array(path: str) -> np.ndarray:
        """
        Deserialize parquet file into a numpy array.

        :param path: The file path where the serialized file is available.
        :return: The deserialized object.
        """
        df = Parqueter.load_pandas_dataframe(path)
        array = cast(np.ndarray, df.to_numpy())
        logger.info(
            "Deserialized parquet file into a numpy array of shape: {}".format(
                array.shape
            )
        )

        inmemory_size_kb = array.nbytes / 1e3
        ondisk_size_kb = os.path.getsize(path) / 1e3
        logger.info(
            f"parquet to ndarray. Memory: {inmemory_size_kb:.2f} kb,"
            f"Disk: {ondisk_size_kb:.2f} kb"
        )

        return array

    @staticmethod
    def load_single_dim_numpy_array(path: str) -> np.ndarray:
        """
        Deserialize parquet file into a single dimensional numpy array.

        :param path: The file path where the serialized file is available.
        :return: The deserialized object.
        """
        array = Parqueter.load_numpy_array(path)
        Contract.assert_true(
            array.ndim == 2 and array.shape[1] == 1,
            message="Expected an array with a single column but received one "
            "with shape: {}".format(array.shape),
        )
        single_dim_array = array.ravel()  # type: np.ndarray
        logger.info(
            "Deserialized parquet file into a single dimensional array of shape: {}".format(
                single_dim_array.shape
            )
        )
        inmemory_size_kb = single_dim_array.nbytes / 1e3
        ondisk_size_kb = os.path.getsize(path) / 1e3
        logger.info(
            f"parquet to ndarray. Memory: {inmemory_size_kb:.2f} kb,"
            f"Disk: {ondisk_size_kb:.2f} kb"
        )

        return single_dim_array

    @staticmethod
    def load_sparse_matrix(path: str) -> sparse.spmatrix:
        """
        Deserialize parquet file into a `scipy.sparse.sp_matrix`.

        :param path: The file path where the serialized file is available.
        :return: The deserialized sparse matrix object in CSR format.
        """
        table_with_metadata = pq.read_table(path)
        shape_x = int(table_with_metadata.schema.metadata.pop(b"shape_x"))
        shape_y = int(table_with_metadata.schema.metadata.pop(b"shape_y"))
        shape = (shape_x, shape_y)
        df = table_with_metadata.to_pandas()  # type: pd.DataFrame
        coo = sparse.coo_matrix((df["data"], (df["row"], df["col"])), shape=shape)
        csr = coo.tocsr()
        inmemory_size_kb = (
            csr.data.nbytes + csr.indptr.nbytes + csr.indices.nbytes
        ) / 1e3
        ondisk_size_kb = os.path.getsize(path) / 1e3
        logger.info(
            f"parquet to spmatrix. Memory: {inmemory_size_kb:.2f} kb,"
            f"Disk: {ondisk_size_kb:.2f} kb"
        )
        return csr
