from typing import List
import pyspark.sql.functions as F
from pyspark.sql import DataFrame as SparkDataFrame
import src.sparkcleaner.helpers.verify as verify


def cast_int_to_date(df: SparkDataFrame, col_name: str,
                     date_format: str = 'yyyyMMdd') -> SparkDataFrame:
    """Convert a date stored as an int to date.

    Parameters
    ----------
    (required) df
        pyspark.sql.DataFrame class
    (required) col_name: str
        int column to be converted to date
    (optional) date_format
        format of int date. Default yyyyMMdd

    Returns
    ----------
    pyspark.sql.DataFrame
        processed date column in place

    Example
    ----------
    my_df = cast_int_to_date(my_df, "MY_COLUMN", 'yyyyMMdd')
    """
    input_vals: List[type] = [SparkDataFrame, str, str]
    expected_vals: List[type] = [type(df),
                                 type(col_name),
                                 type(date_format)]

    verify.verify_func_input(input_vals, expected_vals)

    df = df.withColumn(col_name,
                       F.to_date(F.col(col_name)
                                  .cast('string'),
                                 date_format)
                        .alias(col_name))
    return df
