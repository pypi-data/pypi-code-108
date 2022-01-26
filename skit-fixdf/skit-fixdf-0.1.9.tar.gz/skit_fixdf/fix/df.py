import json
import ast
from typing import Dict, List, Tuple

import pandas as pd

from skit_fixdf import constants as const
from skit_fixdf.fix.datetime import to_datetime


def ensure_columns(fn):
    def wrapper(*args, **kwargs):
        columns = kwargs.get(const.COLUMNS)
        df = args[0]

        if not columns:
            return fn(*args, **kwargs)

        if not isinstance(columns, (list, dict)):
            return fn(*args, **kwargs)

        if not isinstance(df, pd.DataFrame):
            return fn(*args, **kwargs)
        
        if isinstance(columns, dict):
            kwargs[const.COLUMNS] = {k: v for k, v in columns.items() if k in df.columns}
            return fn(*args, **kwargs)

        if all(isinstance(column, tuple) for column in columns):
            kwargs[const.COLUMNS] = filter(lambda col_pairs: col_pairs[0] in df.columns, columns)
        else:
            kwargs[const.COLUMNS] = filter(lambda column: column in df.columns, columns)
        return fn(*args, **kwargs)
    return wrapper


def read_df(df_path: str) -> pd.DataFrame:
    """
    Reads a dataframe from a file.
    :param df_path: Path to the dataframe.
    :return: Dataframe.
    """
    df = pd.read_csv(df_path)
    return df


def rejson(data: str) -> str:
    """
    Re-encode a JSON string.

    :param data: A JSON string.
    :type data: str
    :return: The re-encoded JSON string.
    :rtype: str
    """
    if not isinstance(data, (str, dict)):
        return data

    dict_deserializers = [json.loads, ast.literal_eval]

    if isinstance(data, dict):
        return json.dumps(data, ensure_ascii=False)

    for deserz in dict_deserializers:
        try:
            data = deserz(data)
            return json.dumps(data, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            continue

    raise ValueError(f"Could not decode {data} as json")


@ensure_columns
def json_loads(df: pd.DataFrame, columns: List[str] = list) -> pd.DataFrame:
    for column in columns:
        df[column] = df[column].apply(lambda el: json.loads(el) if isinstance(el, str) else el)
    return df


def is_utterance(utterances: List[dict] = list) -> bool:
    return all(isinstance(utterance, dict) for utterance in utterances) and not pd.isna(utterances)


def fix_utterances(df: pd.DataFrame, column: str) -> pd.DataFrame:
    for i, utterances in df[column].iteritems():
        if i == 0:
            print(utterances, type(utterances))
        if isinstance(utterances, str):
            utterances = json.loads(utterances)

        if not isinstance(utterances, list):
            utterances = []
        elif is_utterance(utterances):
            utterances = [utterances]

        df.at[i, column] = json.dumps(utterances, ensure_ascii=False)
    return df


@ensure_columns
def reorder_cols(df: pd.DataFrame, columns: List[str] = list) -> pd.DataFrame:
    """
    Reorder columns.

    :param df: Dataframe.
    :return: Dataframe.
    """
    return df[columns]


@ensure_columns
def remove_columns(df: pd.DataFrame, columns: List[str] = list) -> pd.DataFrame:
    """
    Removes columns from a dataframe.
    :param df: Dataframe.
    :param columns: List of columns to remove.
    :return: Dataframe.
    """
    df.drop(columns, axis=1, inplace=True)
    return df


@ensure_columns
def remove_rows(
    df: pd.DataFrame, columns: List[str] = list, values: List[str] = list
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


@ensure_columns
def duplicate_columns(df: pd.DataFrame, columns: List[Tuple[str]] = list) -> pd.DataFrame:
    """
    Duplicates columns in a dataframe.

    We take a data-frame: df and column-pairs: [(a, b), ...].
    We duplicate column a (should exist) into b (to be created).

    :param df: Dataframe.
    :param column_pairs: List of column pairs (a, b).
    :return: Dataframe.
    """
    for (column_a, column_b) in columns:
        df[column_b] = df[column_a]
    return df


def rename_columns(df: pd.DataFrame, column_map: Dict[str, str] = dict) -> pd.DataFrame:
    """
    Renames columns in a dataframe.
    :param df: Dataframe.
    :param columns: Dictionary of columns to rename.
    :return: Dataframe.
    """
    df.rename(columns=column_map, inplace=True)
    return df


@ensure_columns
def fix_datetime(df: pd.DataFrame, columns: List[str] = list) -> pd.DataFrame:
    """
    Fixes datetime columns in a dataframe.
    :param df: Dataframe.
    :return: Dataframe.
    """
    for column in columns:
        df[column] = df[column].apply(lambda dt: to_datetime(dt).isoformat() if isinstance(dt, str) else dt)
    return df


@ensure_columns
def min_json_whitespace(df: pd.DataFrame, columns: List[str] = list) -> pd.DataFrame:
    """
    Converts JSON columns to have minimum whitespace.

    :param df: Dataframe.
    :return: Dataframe.
    """
    for column in columns:
        df[column] = df[column].apply(rejson)
    return df
