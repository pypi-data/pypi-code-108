from typing import Dict, Optional, List, Sequence, Hashable, Union
from pathlib import Path
import pandas as pd

from common_client_scheduler import ExportRequest
from terality.exceptions import TeralityClientError
from terality_serde import StructType

from . import ClassMethod, Struct
from terality._terality.data_transmitter import S3


class ClassMethodDF(ClassMethod):
    _class_name: str = StructType.DATAFRAME
    _pandas_class = pd.DataFrame
    _additional_class_methods = ClassMethod._additional_class_methods | {
        "from_dict",
        "from_records",
    }


def _make_export_request(path: str, storage_options: Optional[Dict] = None) -> ExportRequest:
    if not isinstance(path, str):
        raise TeralityClientError("Export methods only support a str path.")

    if path.startswith("s3://"):
        bucket = path[5:].split("/", maxsplit=1)[0]
        aws_region = S3.client().get_bucket_location(Bucket=bucket)["LocationConstraint"]
        # For the us-east-1 region, this call returns None. Let's fix that.
        # Reference: https://github.com/aws/aws-cli/issues/3864 (the same is observed with boto3)
        if aws_region is None:
            aws_region = "us-east-1"
    elif path.startswith("abfs://"):
        aws_region = None
    else:
        # If path is local, convert it to absolute path
        aws_region = None
        path = _make_absolute_path(path)

    return ExportRequest(path=path, aws_region=aws_region, storage_options=storage_options)


def _make_absolute_path(path: str) -> str:
    return str(Path(path).resolve())


class DataFrame(Struct, metaclass=ClassMethodDF):
    """
    A terality DataFrame to handle two-dimensional, size-mutable, and potentially heterogeneous tabular data.
    This behaves exactly like a pandas.DataFrame: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html.

    The most common ways to build a terality DataFrame are the following:

    - reading from a file:
    >>> df = terality.read_csv("path/to/my/file.csv")

    - instantiating from a pandas.DataFrame:
    >>> df = terality.DataFrame(df_pd)

    - using the constructor:
    >>> df = terality.DataFrame({"col1": [0, 1, 2], "col2": ["A", "B", "C"]})
    >>> df
      col1 col2
    0     0    A
    1     1    B
    2     2    C
    """

    _class_name: str = StructType.DATAFRAME
    _pandas_class_instance = pd.DataFrame()
    _additional_methods = Struct._additional_methods | {
        "to_csv_folder",
        "to_parquet_folder",
    }
    _args_to_replace: dict = {
        # "to_csv" : (0, ExportRequest),
        "to_excel": (0, _make_export_request)
    }

    def _on_missing_attribute(self, item: str):
        return self._call_method(None, "df_col_by_attribute_access", item)

    def __iter__(self):
        # Iterating on a `DataFrame` is the same as iterating on its columns.
        return self.columns.__iter__()

    def to_csv(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        path_or_buf: str,
        sep: str = ",",
        na_rep: str = "",
        float_format: Optional[str] = None,
        columns: Optional[Sequence[Optional[Hashable]]] = None,
        header: Union[bool, List[str]] = True,
        index: bool = True,
        index_label: Optional[Union[str, Sequence, bool]] = None,
        mode: str = "w",
        encoding: Optional[str] = None,
        compression: Union[str, dict] = "infer",
        quoting: Optional[int] = None,
        quotechar: str = '"',
        line_terminator: Optional[str] = None,
        chunksize: Optional[int] = None,
        date_format: Optional[str] = None,
        doublequote: bool = True,
        escapechar: Optional[str] = None,
        decimal: str = ".",
        errors: str = "strict",
        storage_options: Optional[Dict] = None,
    ) -> Optional[str]:
        export_request = _make_export_request(path_or_buf, storage_options)
        return self._call_method(
            None,
            "to_csv",
            export_request,
            sep=sep,
            na_rep=na_rep,
            float_format=float_format,
            columns=columns,
            header=header,
            index=index,
            index_label=index_label,
            mode=mode,
            encoding=encoding,
            compression=compression,
            quoting=quoting,
            quotechar=quotechar,
            line_terminator=line_terminator,
            chunksize=chunksize,
            date_format=date_format,
            doublequote=doublequote,
            escapechar=escapechar,
            decimal=decimal,
            errors=errors,
            storage_options=storage_options,
        )

    def to_csv_folder(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        path_or_buf: str,
        num_files: Optional[int] = None,
        num_rows_per_file: Optional[int] = None,
        in_memory_file_size: Optional[int] = None,
        with_leading_zeros: bool = False,
        sep: str = ",",
        na_rep: str = "",
        float_format: Optional[str] = None,
        columns: Optional[Sequence[Optional[Hashable]]] = None,
        header: Union[bool, List[str]] = True,
        index: bool = True,
        index_label: Optional[Union[str, Sequence, bool]] = None,
        mode: str = "w",
        encoding: Optional[str] = None,
        compression: Union[str, dict] = "infer",
        quoting: Optional[int] = None,
        quotechar: str = '"',
        line_terminator: Optional[str] = None,
        chunksize: Optional[int] = None,
        date_format: Optional[str] = None,
        doublequote: bool = True,
        escapechar: Optional[str] = None,
        decimal: str = ".",
        errors: str = "strict",
        storage_options: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Store the DataFrame in several CSV files. Exactly one of num_files, num_rows_per_file, file_size must be provided.
        The number of files to produce is deduced from the parameter filled.
        The path basename must contain the character *, that will be replaced by file number when producing files.
        If the path contains a non-existing folder, it is created.
        Leading zeros can be added to file numbers so each filename will have the same length.

        NOTE: This method has a specific documentation https://docs.terality.com/getting-terality/api-reference/write-to-multiple-files
        which should be updated if needed.
        """

        export_request = _make_export_request(path_or_buf, storage_options)
        return self._call_method(
            None,
            "to_csv_folder",
            export_request,
            num_files=num_files,
            num_rows_per_file=num_rows_per_file,
            in_memory_file_size=in_memory_file_size,
            with_leading_zeros=with_leading_zeros,
            sep=sep,
            na_rep=na_rep,
            float_format=float_format,
            columns=columns,
            header=header,
            index=index,
            index_label=index_label,
            mode=mode,
            encoding=encoding,
            compression=compression,
            quoting=quoting,
            quotechar=quotechar,
            line_terminator=line_terminator,
            chunksize=chunksize,
            date_format=date_format,
            doublequote=doublequote,
            escapechar=escapechar,
            decimal=decimal,
            errors=errors,
            storage_options=storage_options,
        )

    def to_parquet(
        self,
        path: str,
        engine: str = "auto",
        compression: Optional[str] = "snappy",
        index: Optional[bool] = None,
        partition_cols: Optional[List[str]] = None,
        storage_options: Optional[Dict] = None,
    ):

        return self._call_method(
            None,
            "to_parquet",
            _make_export_request(path, storage_options),
            engine=engine,
            compression=compression,
            index=index,
            partition_cols=partition_cols,
            storage_options=storage_options,
        )

    def to_parquet_folder(  # pylint: disable=too-many-arguments
        self,
        path: str,
        num_files: Optional[int] = None,
        num_rows_per_file: Optional[int] = None,
        in_memory_file_size: Optional[int] = None,
        with_leading_zeros: bool = False,
        engine: str = "auto",
        compression: Optional[str] = "snappy",
        index: Optional[bool] = None,
        partition_cols: Optional[List[str]] = None,
        storage_options: Optional[Dict] = None,
    ):
        """
        Store the DataFrame in several parquet files. Exactly one of num_files, num_rows_per_file, file_size must be provided.
        The number of files to produce is deduced from the parameter filled.
        The path basename must contain the character *, that will be replaced by file number when producing files.
        If the path contains a non-existing folder, it is created.
        Leading zeros can be added to file numbers so each filename will have the same length.

        NOTE: This method has a specific documentation https://docs.terality.com/getting-terality/api-reference/write-to-multiple-files
        which should be updated if needed.
        """

        return self._call_method(
            None,
            "to_parquet_folder",
            _make_export_request(path, storage_options),
            engine=engine,
            compression=compression,
            index=index,
            partition_cols=partition_cols,
            storage_options=storage_options,
            num_files=num_files,
            num_rows_per_file=num_rows_per_file,
            in_memory_file_size=in_memory_file_size,
            with_leading_zeros=with_leading_zeros,
        )

    def to_dict(self, orient: str = "dict", into: type = dict):
        pd_df = self._call_method(None, "to_pandas")
        return pd_df.to_dict(orient=orient, into=into)

    def info(
        self,
        verbose: Optional[bool] = None,
        max_cols: Optional[int] = None,
        memory_usage: Optional[Union[bool, str]] = None,
        null_counts: Optional[bool] = None,
    ):

        info = self._call_method(
            None,
            "info",
            verbose=verbose,
            max_cols=max_cols,
            memory_usage=memory_usage,
            null_counts=null_counts,
        )
        print(info)
