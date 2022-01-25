import numpy as np
import pandas as pd
from pandas.core.groupby import SeriesGroupBy, DataFrameGroupBy
from terality_serde import SerializableEnum


# This class needs to be common to client / scheduler / worker.
class IndexType(str, SerializableEnum):
    """
    Technical types names of supported index sub classes.
    """

    INDEX = "index"
    MULTI_INDEX = "multi_index"
    DATETIME_INDEX = "datetime_index"
    INT64_INDEX = "int64_index"
    FLOAT64_INDEX = "float64_index"


class StructType(str, SerializableEnum):
    """
    Technical types names of pandas supported structures, excluding index.
    """

    DATAFRAME = "dataframe"
    SERIES = "series"
    DATAFRAME_GROUPBY = "dataframe_groupby"
    SERIES_GROUPBY = "series_groupby"
    NDARRAY = "ndarray"
    TOP_LEVEL = "top_level"


STRUCT_TYPE_TO_PANDAS_CLASS = {
    IndexType.INDEX: pd.Index,
    IndexType.INT64_INDEX: pd.Int64Index,
    IndexType.FLOAT64_INDEX: pd.Float64Index,
    IndexType.DATETIME_INDEX: pd.DatetimeIndex,
    IndexType.MULTI_INDEX: pd.MultiIndex,
    StructType.NDARRAY: np.ndarray,
    StructType.SERIES: pd.Series,
    StructType.DATAFRAME: pd.DataFrame,
    StructType.SERIES_GROUPBY: SeriesGroupBy,
    StructType.DATAFRAME_GROUPBY: DataFrameGroupBy,
    StructType.TOP_LEVEL: pd,
}
