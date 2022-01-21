from typing import Any, Callable, Dict

import pandas as pd
import pyarrow
from pyarrow import parquet

from common_client_scheduler import (
    Display,
    ExportResponse,
    StructRef,
    PandasIndexMetadata,
    PandasSeriesMetadata,
    PandasDFMetadata,
    NDArrayMetadata,
    AwsCredentials,
)
from common_client_scheduler.structs import IndexType, ParquetMetadata
from terality_serde import StructType
from terality_serde.json_encoding import (
    _endecode_json_index_inplace,
    _endecode_json_columns_inplace,
)

from terality._terality.data_transfers.s3 import copy_to_user_s3_bucket

from ..utils.azure import test_for_azure_libs, parse_azure_filesystem
from .. import global_client
from ...exceptions import TeralityClientError


def _deserialize_display(
    aws_credentials: AwsCredentials, to_display: Display
):  # pylint: disable=unused-argument,useless-return
    # No need to force it in package dependencies, if it gets called it means we are in a Jupyter Notebook
    # and and this dependency is present
    # noinspection PyUnresolvedReferences
    from IPython.display import display, HTML

    display(HTML(to_display.value))


def _deserialize_export(aws_credentials: AwsCredentials, export: ExportResponse) -> None:
    path = export.path
    transfer_id = export.transfer_id
    if path.startswith("s3://"):
        copy_to_user_s3_bucket(aws_credentials, transfer_id, export.aws_region, path)
    elif path.startswith("abfs://") or path.startswith("az://"):
        test_for_azure_libs()
        from ..data_transfers.azure import copy_to_azure_datalake

        storage_account_name, container, path = parse_azure_filesystem(path, export.storage_options)
        copy_to_azure_datalake(
            aws_credentials=aws_credentials,
            transfer_id=transfer_id,
            aws_region=export.aws_region,
            storage_account_name=storage_account_name,
            container=container,
            path_template=path,
        )
    elif path.startswith("gs://"):
        raise TeralityClientError(
            "Currently, Terality does not support GCP storage. Please use AWS S3 or Azure paths."
        )
    else:
        global_client().data_transfer().download_to_local_files(
            aws_credentials, transfer_id, path, export.is_folder, export.with_leading_zeros
        )


def _download_df(
    aws_credentials: AwsCredentials,
    transfer_id: str,
    metadata: ParquetMetadata,
) -> pd.DataFrame:
    bytes_io = global_client().data_transfer().download_to_bytes(aws_credentials, transfer_id)

    df = pd.read_parquet(bytes_io)
    # range index get dropped by read_parquet on a df with no cols
    if df.shape[0] == 0:
        file_schema = parquet.read_schema(pyarrow.BufferReader(bytes_io.getvalue()))
        pandas_metadata = file_schema.pandas_metadata
        index_metadata = pandas_metadata["index_columns"]
        if len(index_metadata) == 1 and isinstance(index_metadata[0], dict):
            range_index = index_metadata[0]
            if range_index["kind"] == "range":
                index = pd.RangeIndex(
                    start=range_index["start"],
                    stop=range_index["stop"],
                    step=range_index["step"],
                    name=range_index["name"],
                )
                return pd.DataFrame(index=index)
    _endecode_json_index_inplace(df, metadata.index.encodings, encode=False)
    _endecode_json_columns_inplace(df, metadata.cols.encodings, encode=False)

    df.columns = metadata.cols.col_names
    # mypy does not understand that it's not a basic setattre and that df.columns is not a list of str
    df.columns.name = metadata.cols.col_names_name  # type: ignore

    if isinstance(df.index, pd.MultiIndex):
        df.index.names = metadata.index.names
    df.index.name = metadata.index.name
    if metadata.index.datetime_index_freq is not None:
        assert isinstance(df.index, pd.DatetimeIndex)
        df.index.freq = metadata.index.datetime_index_freq

    return df


def _download_ndarray_from_metadata(
    aws_credentials: AwsCredentials, ndarray_metadata: NDArrayMetadata
):
    # noinspection PyTypeChecker
    # TODO use np.load, but we have to upload accordingly within scheduler ndarray_to_numpy_metadata.
    df = _download_df(
        aws_credentials, ndarray_metadata.transfer_id, ndarray_metadata.parquet_metadata
    )
    assert len(df.columns) == 1
    return df.iloc[:, 0].to_numpy()


def _download_index_from_metadata(
    aws_credentials: AwsCredentials, index_metadata: PandasIndexMetadata
) -> pd.Index:
    df = _download_df(aws_credentials, index_metadata.transfer_id, index_metadata.parquet_metadata)
    return df.index


def _download_series_from_metadata(
    aws_credentials: AwsCredentials, series_metadata: PandasSeriesMetadata
) -> pd.Series:
    df = _download_df(
        aws_credentials, series_metadata.transfer_id, series_metadata.parquet_metadata
    )
    series = df.iloc[:, 0]
    return series


def _download_df_from_metadata(
    aws_credentials: AwsCredentials, df_metadata: PandasDFMetadata
) -> pd.DataFrame:
    df = _download_df(aws_credentials, df_metadata.transfer_id, df_metadata.parquet_metadata)
    return df


_decoder: Dict[Any, Callable[[AwsCredentials, Any], Any]] = {
    NDArrayMetadata: _download_ndarray_from_metadata,
    PandasIndexMetadata: _download_index_from_metadata,
    PandasSeriesMetadata: _download_series_from_metadata,
    PandasDFMetadata: _download_df_from_metadata,
    Display: _deserialize_display,
    ExportResponse: _deserialize_export,
}


def decode(credentials_fetcher: AwsCredentials, obj):  # pylint: disable=invalid-name
    from terality import (
        NDArray,
        Index,
        Int64Index,
        Float64Index,
        DatetimeIndex,
        MultiIndex,
        Series,
        DataFrame,
    )  # To avoid circular dependencies
    from terality._terality.terality_structures import DataFrameGroupBy, SeriesGroupBy

    structs = {
        IndexType.INDEX: Index,
        IndexType.INT64_INDEX: Int64Index,
        IndexType.FLOAT64_INDEX: Float64Index,
        IndexType.DATETIME_INDEX: DatetimeIndex,
        IndexType.MULTI_INDEX: MultiIndex,
        StructType.NDARRAY: NDArray,
        StructType.SERIES: Series,
        StructType.DATAFRAME: DataFrame,
        StructType.SERIES_GROUPBY: SeriesGroupBy,
        StructType.DATAFRAME_GROUPBY: DataFrameGroupBy,
    }

    if isinstance(obj, StructRef):
        # noinspection PyProtectedMember
        # NOTE: hash(StrEnum.X) = hash(StrEnum.X.value)
        return structs[obj.type]._new(id_=obj.id)  # type: ignore
    if type(obj) in _decoder:
        return _decoder[type(obj)](credentials_fetcher, obj)
    return obj
