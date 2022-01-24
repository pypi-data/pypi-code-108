import pathlib
import typing as t

import pandas as pd  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from tktl.core.loggers import LOG

JSONObject = t.Dict[t.AnyStr, t.Any]
JSONArray = t.List[t.Any]
JSONStructure = t.Union[JSONArray, JSONObject]


def coerce_dataframe_to_series(df: pd.DataFrame) -> t.Union[pd.DataFrame, pd.Series]:
    if len(df.columns) == 1:
        # Since we store dataframes in parquet files, we assume that a
        # one column dataframe used to be a Series.
        return df.iloc[:, 0]
    return df


def coerce_series_to_dataframe(obj: t.Union[pd.DataFrame, pd.Series]) -> pd.DataFrame:
    if isinstance(obj, pd.Series):
        return pd.DataFrame({str(obj.name): obj})
    if len(obj.columns) == 1:
        LOG.error(
            "Storing 1 column dataframe, this will become a Series on the way back"
        )
    return obj


def get_number_of_rows_in_chunk(path: pathlib.Path, bytes_per_chunk: int) -> int:
    """get_chunk_size.
    Calculate number of rows per chunk. This file does _not_ read the
    data from the parquet file.

    If the file is 1024 bytes and every chunk is 500 bytes we want to have
    3 chunks. Let's say that there are 16 rows in the file, then the desired
    result is 6 rows per chunk.

    Parameters
    ----------
    path : pathlib.Path
        path to the parquet file
    bytes_per_chunk : int
        bytes that are supposed to be in every chunk

    Returns
    -------
    int - number of rows every chunk contains

    """
    file_size_in_bytes = path.stat().st_size
    pq_file = pq.ParquetFile(path)
    number_of_rows = pq_file.metadata.num_rows

    chunks = file_size_in_bytes // bytes_per_chunk + 1

    return number_of_rows // chunks + 1
