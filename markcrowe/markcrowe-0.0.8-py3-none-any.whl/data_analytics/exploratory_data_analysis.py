# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from pandas import DataFrame
from pandas import Series

Q1 = 0.25
Q2 = 0.5
Q3 = 0.75
TUKEY_IQR_SCALE = 1.5


def calculate_iqr(q1: float, q3: float) -> float:
    """
    Calculate the interquartile range
    :param q1: first quantile
    :param q3: third quantile
    :return: interquartile range
    """
    return q3 - q1


def calculate_iqr_of_column(dataframe: DataFrame, column_label: str) -> float:
    """
    Calculate the interquartile range
    :param dataframe: DataFrame
    :param column_label: The Column to use for calculating interquartile range
    :return: interquartile range
    """
    q1, q3 = calculate_quantile_bounds(dataframe, column_label)
    return q3 - q1


def calculate_missing_value_statistics(dataframe: DataFrame) -> DataFrame:
    missing_stats_dataframe = DataFrame(
        {
            'Missing': dataframe.isnull().sum(),
            '% Missing': dataframe.isnull().sum() / len(dataframe) * 100
        })
    missing_stats_dataframe = missing_stats_dataframe[missing_stats_dataframe['Missing'] > 0]
    return missing_stats_dataframe.sort_values(by='Missing', ascending=False)


def calculate_outlier_limits(dataframe: DataFrame, column_label: str) -> tuple:
    """
    Calculate the limits of outliers
    :param dataframe: DataFrame
    :param column_label: The Column to use for removing outliers
    :return: tuple of lower and upper limits
    """
    q1, q3 = calculate_quantile_bounds(dataframe, column_label)
    iqr = calculate_iqr(q1, q3)
    lower_limit = q1 - TUKEY_IQR_SCALE * iqr
    upper_limit = q3 + TUKEY_IQR_SCALE * iqr
    return lower_limit, upper_limit


def calculate_quantile_bounds(dataframe: DataFrame, column_label: str) -> tuple:
    """
    Calculates the first (q1) and third (q3) quantiles of the column
    :param dataframe: DataFrame
    :param column_label: The Column to use first and third quantiles
    :return: the first (q1) and third (q3) quantiles of the column
    """
    q1 = dataframe[column_label].quantile(Q1)
    q3 = dataframe[column_label].quantile(Q3)
    return q1, q3


def count_outliers(dataframe: DataFrame, column_label: str) -> int:
    """
    Get the count of outliers
    :param dataframe: DataFrame
    :param column_label: The Column to use for removing outliers
    :return: count of outliers
    """
    return get_outliers_dataframe(dataframe, column_label).shape[0]


def get_expected_range_dataframe(dataframe: DataFrame, column_label: str) -> DataFrame:
    """
    Get expected range of rows by excluding outliers
    :param dataframe: DataFrame
    :param column_label: The Column to use for removing outliers
    :return: DataFrame of expected range
    """
    lower_limit, upper_limit = calculate_outlier_limits(
        dataframe, column_label)
    return dataframe[(dataframe[column_label] >= lower_limit) & (dataframe[column_label] <= upper_limit)]


def get_names_of_columns_with_null_values(dataframe: DataFrame) -> list:
    """
    Get the names of columns with null values
    :param dataframe: DataFrame
    :return: names of columns with null values
    """
    return dataframe.columns[dataframe.isna().any()].tolist()


def get_outliers_dataframe(dataframe: DataFrame, column_label: str) -> DataFrame:
    """
    Get outliers of rows by excluding expected range
    :param dataframe: DataFrame
    :param column_label: The Column to use for removing outliers
    :return: DataFrame of outliers
    """
    lower_limit, upper_limit = calculate_outlier_limits(
        dataframe, column_label)
    return dataframe[(dataframe[column_label] < lower_limit) | (dataframe[column_label] > upper_limit)]


def has_outliers(dataframe: DataFrame, column_label: str) -> bool:
    """
    Check if the dataframe has outliers in the column
    :param dataframe: DataFrame
    :param column_label: The Column to use for checking
    :return: True if the column has outliers
    """
    return count_outliers(dataframe, column_label) > 0


def is_numeric_data_type_column(series: Series) -> bool:
    """
    Check if the column is a numeric data type
    :param series: Series the array to use for checking
    :return: True if the column is a numeric data type
    """
    NUMERIC_DATA_TYPE_CHARACTER_CODES = 'ifu'  # i	signed integer, u	unsigned integer, f	floating-point
    return series.dtype.kind in NUMERIC_DATA_TYPE_CHARACTER_CODES


def is_single_value_column(dataframe: DataFrame, column_label: str) -> bool:
    """
    Check if the column has only one value
    :param dataframe: DataFrame
    :param column_label: The Column to use for checking
    :return: True if the column has only one value
    """
    return dataframe[column_label].isnull().sum() == 0 and dataframe[column_label].nunique() == 1


def is_single_value_series(series: Series) -> bool:
    """
    Check if the column has only one value
    :param series: Series the array to use for checking
    :return: True if the column has only one value
    """
    return series.isnull().sum() == 0 and series.nunique() == 1
