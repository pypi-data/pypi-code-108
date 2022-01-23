import json
from typing import Dict, List, Tuple

import pandas as pd

from skit_fixdf import constants as const
from skit_fixdf.fix.datetime import to_datetime


def read_df(df_path: str) -> pd.DataFrame:
    """
    Reads a dataframe from a file.
    :param df_path: Path to the dataframe.
    :return: Dataframe.
    """
    df = pd.read_csv(df_path)
    return df


# TODO: goes somewhere else
def rejson(data: str) -> str:
    """
    Re-encode a JSON string.

    :param data: A JSON string.
    :type data: str
    :return: The re-encoded JSON string.
    :rtype: str
    """
    return json.dumps(json.loads(data), ensure_ascii=False)


def reorder_cols(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Reorder columns.

    :param df: Dataframe.
    :return: Dataframe.
    """
    return df[columns]


def remove_columns(df: pd.DataFrame, required: List[str]) -> pd.DataFrame:
    """
    Removes columns from a dataframe.
    :param df: Dataframe.
    :param columns: List of columns to remove.
    :return: Dataframe.
    """
    columns = df.columns.difference(required)
    df.drop(columns, axis=1, inplace=True)
    return df


def remove_rows(
    df: pd.DataFrame, columns: List[str], values: List[str]
) -> pd.DataFrame:
    """
    Removes rows from a dataframe.

    :param df: Dataframe.
    :param columns: List of columns to check.
    :param values: List of values to remove.
    :return: Dataframe.
    """
    for column in columns:
        df = df[~df[column].isin(values)]
    return df


def duplicate_columns(df: pd.DataFrame, column_pairs: List[Tuple[str]]) -> pd.DataFrame:
    """
    Duplicates columns in a dataframe.

    We take a data-frame: df and column-pairs: [(a, b), ...].
    We duplicate column a (should exist) into b (to be created).

    :param df: Dataframe.
    :param column_pairs: List of column pairs (a, b).
    :return: Dataframe.
    """
    for (column_a, column_b) in column_pairs:
        df[column_b] = df[column_a]
    return df


def rename_columns(df: pd.DataFrame, column_map: Dict[str, str]) -> pd.DataFrame:
    """
    Renames columns in a dataframe.
    :param df: Dataframe.
    :param columns: Dictionary of columns to rename.
    :return: Dataframe.
    """
    df.rename(columns=column_map, inplace=True)
    return df


def fix_datetime(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Fixes datetime columns in a dataframe.
    :param df: Dataframe.
    :return: Dataframe.
    """
    for column in columns:
        df[column] = df[column].apply(lambda dt: to_datetime(dt).isoformat())
    return df


def min_json_whitespace(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Converts JSON columns to have minimum whitespace.

    :param df: Dataframe.
    :return: Dataframe.
    """
    for column in columns:
        df[column] = df[column].apply(rejson)
    return df
