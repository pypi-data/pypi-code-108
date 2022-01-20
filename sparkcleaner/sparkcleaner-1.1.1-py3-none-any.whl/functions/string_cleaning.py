from typing import List, Optional, Type
import pyspark.sql.functions as F
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.types import DataType
import src.sparkcleaner.helpers.verify as verify


def remove_leading_zeros(df: SparkDataFrame,
                         col_name: str,
                         maintain_type: bool = True) -> SparkDataFrame:
    """Remove leading zeros from column using regex.

    Parameters
    ----------
    (required) df: pyspark.sql.DataFrame
        Pyspark DataFrame containing column to be processed
    (required) col_name: str
        name of column to remove leading zeros from
    (optional) maintain_type: bool = True
        If false, returns col as str.
        If true, returns col as type before function call

    Returns
    ----------
    pyspark.sql.DataFrame
        processed column in place

    See Also
    ----------
    pyspark.sql.functions.regexp_replace()
    pyspark.sql.Column.cast()

    Example
    ----------
    my_df = remove_leading_zeros(my_df, "MY_COL", False)
    """
    _rlz_func_verify_input_types(df, col_name, maintain_type)

    original_type: DataType = df.schema[col_name].dataType
    df = df.withColumn(col_name, F.regexp_replace(F.col(col_name),
                                                  r'^[0]*', ""))
    df = _if_maintain_type_cast_original_type(df, col_name,
                                              maintain_type, original_type)
    return df


def _rlz_func_verify_input_types(df: SparkDataFrame,
                        col_name: str,
                        maintain_type: bool) -> None:
    input_vals: List[type] = [SparkDataFrame, str, bool]
    expected_vals: List[type] = [type(df),
                                 type(col_name),
                                 type(maintain_type)]

    verify.verify_func_input(input_vals, expected_vals)


def _if_maintain_type_cast_original_type(df: SparkDataFrame,
                                         col_name: str,
                                         maintain_type: bool,
                                         original_type: DataType) -> SparkDataFrame:
    if maintain_type:
        df = df.withColumn(col_name,
                           F.col(col_name)
                            .cast(original_type)
                            .alias(col_name))                      
    return df


def keep_alphanumeric_string(df: SparkDataFrame,
                             col_name: str,
                             maintain_type: bool = True,
                             keep_spaces: bool = True) -> SparkDataFrame:
    """Removes all non-alphanumeric characters from column using regex
        Parameters
    ----------
    (required) df: pyspark.sql.DataFrame
        Pyspark DataFrame containing column to be processed
    (required) col_name: str
        name of column to remove non-alphanumeric characters from
    (optional) maintain_type: bool = True
        If false, returns col as str.
        If true, returns col as type before function call
    (optional) keep_spaces: bool = True
        If false, removes all spaces from col
        If true, leaves spaces in col

    Returns
    ----------
    pyspark.sql.DataFrame
        processed column in place

    See Also
    ----------
    pyspark.sql.functions.regexp_replace()
    pyspark.sql.Column.cast()

    Example
    ----------
    my_df = keep_alphanumeric_string(my_df, "MY_COL", False)
    """
    _kes_func_verify_input_types(df, col_name, maintain_type, keep_spaces)

    original_type: DataType = df.schema[col_name].dataType

    regex: str = _set_regex(keep_spaces)
    df = df.withColumn(col_name, F.regexp_replace(F.col(col_name),
                                                  regex, ""))
    df = _if_maintain_type_cast_original_type(df, col_name,
                                              maintain_type, original_type)
    return df


def _set_regex(keep_spaces: bool) -> str:
    if keep_spaces:
        regex: str = r'[^A-Za-z0-9 ]'  # spaces & alphanumeric
    else:
        regex: str = r'[^A-Za-z0-9]'  # alphanumeric
    return regex


def _kes_func_verify_input_types(df: SparkDataFrame,
                                 col_name: str,
                                 maintain_type: bool,
                                 keep_spaces: bool) -> None:
    input_vals: List[type] = [SparkDataFrame, str, bool, bool]
    expected_vals: List[type] = [type(df),
                                 type(col_name),
                                 type(maintain_type),
                                 type(keep_spaces)]

    verify.verify_func_input(input_vals, expected_vals)
