"""Spark utility functions."""
import itertools
import functools
from typing import (
    Any,
    Callable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import pandas as pd
from pyspark.sql import (
    Column as SparkCol,
    DataFrame as SparkDF,
    functions as F,
    Window,
    WindowSpec,
)
from pyspark.sql.types import StructType
from pyspark.sql.functions import pandas_udf, PandasUDFType

from ons_utils.generic import list_convert


def convert_to_spark_col(s: Union[str, SparkCol]) -> SparkCol:
    """Convert strings to Spark Columns, otherwise returns input."""
    if isinstance(s, str):
        return F.col(s)
    elif isinstance(s, SparkCol):
        return s
    else:
        raise ValueError(
            "expecting a string or pyspark column but received obj"
            f" of type {type(s)}"
        )


def convert_to_pandas_udf(
    func: Callable[..., pd.DataFrame],
    schema: Union[StructType, str],
    groups: Sequence[str],
    keep_index: bool = False,
    args: Optional[Sequence[Any]] = None,
    kwargs: Optional[Mapping[str, Any]] = None,
) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Convert the given function to a pyspark pandas_udf.

    Parameters
    ----------
    func : callable
        The function to convert to a pandas_udf. Must take a pandas
        dataframe as it's first argument.
    schema : StructType or str
        The schema for the output of the pandas_udf as either a
        StructType or a str schema in the DDL format i.e. ("col1 string,
        col2 integer, col3 timestamp").
    groups : sequence of str
        The column keys that define the groupings in the data. Needed
        here so it is available in the scope of the pandas_udf which can
        only accept a single pandas dataframe as an input.
    keep_index : bool, default False
        Set to True if the output from ``func`` returns a pandas
        dataframe with columns in the index that should be kept. Keep
        False if ``func`` already returns a pandas dataframe with no
        values in the index.
    args : sequence, optional
        The positional arguments to be unpacked into ``func``.
    kwargs : mapping, optional
        The keyword arguments to be unpacked into ``func``.

    Returns
    -------
    Callable
        A GROUPED_MAP pandas_udf that accepts a single pandas dataframe
        and returns a pandas dataframe.
    """
    args = [] if not args else args
    kwargs = {} if not kwargs else kwargs

    # As pandas_udfs with function type GROUPED_MAP must take either one
    # argument (data) or two arguments (key, data), it needs to be
    # defined as a nested function so that it has access to the
    # parameters in the enclosing scope.
    @functools.wraps(func)
    @pandas_udf(schema, PandasUDFType.GROUPED_MAP)
    def wrapped_udf(df):
        result = func(df, *args, **kwargs)

        # Reset the index before returning.
        if keep_index:
            result = result.reset_index()

        # Because df is a single group we cast the first value for each
        # group key across the whole column in the output.
        groups_df = (
            pd.DataFrame(index=result.index, columns=groups)
            .fillna(df.loc[0, groups])
        )

        return pd.concat([groups_df, result], axis=1)

    return wrapped_udf


def get_ddl_schema(fields: Sequence[Tuple[str, str]]) -> str:
    """Get the ddl style schema from (name, dtype) fields.

    Parameters
    ----------
    dtypes : sequence of tuple
        List of (name, dtype) tuples, similar to the output of
        pyspark.sql.DataFrame.dtypes.

    Returns
    -------
    str
        The ddl schema.
    """
    ddl_schema = '\n'.join([f'{name} {dtype},' for name, dtype in fields])
    # Remove the last comma.
    return ddl_schema[:-1]


def get_fields(
    df: SparkDF,
    selection: Optional[Sequence[str]] = None,
) -> Sequence[Tuple[str, str]]:
    """Get the (name, dtype) fields for the dataframe.

    Parameters
    ----------
    selection : sequence of str, optional
        The selection of columns to return fields for.

    Returns
    -------
    sequence of tuple
        In the format (name, dtype) for each selected column.
    """
    fields = dict(df.dtypes)

    if selection:
        return [(col, fields.get(col)) for col in selection]
    else:
        return fields


def map_col(col_name: str, mapping: Mapping[Any, Any]) -> SparkCol:
    """Map PySpark column using Python mapping."""
    map_expr = F.create_map([
        F.lit(x)
        if not is_list_or_tuple(x)
        # To handle when the value is a list or tuple.
        else F.array([F.lit(i) for i in x])
        # Convert mapping to list.
        for x in itertools.chain(*mapping.items())
    ])
    return map_expr[F.col(col_name)]


def is_list_or_tuple(x):
    """Return True if list or tuple."""
    return isinstance(x, tuple) or isinstance(x, list)


def get_window_spec(
    groups: Union[str, Sequence[str]] = None
) -> WindowSpec:
    """Return WindowSpec partitioned by groups, defaulting to whole df.

    Note that if groups is None, then the window will be over the whole
    DataFrame and the partition will be 1. Only suitable for small
    DataFrames - use with caution on large DataFrames and make sure
    it is repartitioned if a new column is created.
    """
    return (
        Window.partitionBy(list_convert(groups)) if groups
        else Window.partitionBy()
    )


def to_list(df: SparkDF) -> List[Union[Any, List[Any]]]:
    """Convert Spark DF to a list.

    Returns
    -------
    list or list of lists
        If the input DataFrame has a single column then a list of column
        values will be returned. If the DataFrame has multiple columns
        then a list of row data as lists will be returned.
    """
    if len(df.columns) == 1:
        return df.toPandas().squeeze().tolist()
    else:
        return df.toPandas().values.tolist()


def map_column_names(df: SparkDF, mapper: Mapping[str, str]) -> SparkDF:
    """Map column names to the given values in the mapper.

    If the column name is not in the mapper the name doesn't change.
    """
    cols = [
        F.col(col_name).alias(mapper.get(col_name, col_name))
        for col_name in df.columns
    ]
    return df.select(*cols)


def get_hive_table_columns(spark, table_path) -> List[str]:
    """Return the column names for the given Hive table."""
    return to_list(spark.sql(f'SHOW columns in {table_path}'))


def transform(self, f, *args, **kwargs):
    """Chain Pyspark function."""
    return f(self, *args, **kwargs)


def get_first_group(df: SparkDF, groups: Sequence[str]) -> SparkDF:
    """Return a sample pyspark dataframe filtered to the first group."""
    row = df.select(groups).head(1)[0]
    query = " AND ".join([f"{group}=='{row[group]}'" for group in groups])
    return df.filter(query)
