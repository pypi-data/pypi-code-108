# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from sklearn.base import TransformerMixin


def get_pandas_columns_types_mapping(df: pd.DataFrame) -> Dict[str, np.dtype]:
    columns_types_mapping = {}  # type: Dict[str, np.dtype]
    for col in df.columns:
        columns_types_mapping[col] = df[col].dtype
    return columns_types_mapping


def generate_new_column_names(columns: List[str]) -> Tuple[List[str], List[str]]:
    """
    Generates new column prefixes for using in Engineered feature names. In case column names are not
    specified by the user, this generates column names of the format `C<index>` where `index` is
    incremented.

    :param columns: Input column names.
    :return: A tuple of raw feature names and new column names.
    """
    Contract.assert_non_empty(value=columns, name='columns',
                              reference_code=ReferenceCodes._NEW_COLUMN_GENERATION_ATLEAST_ONE_COLUMN_EXPECTED)

    generated_column_name_prefix = 'C'
    index_raw_columns = 0

    new_column_names = []  # type: List[str]
    raw_feature_names = []  # type: List[str]
    for column in columns:
        # If column name is not an integer, then record it in the raw feature name
        if not isinstance(column, (int, np.integer)):
            raw_feature_names.append(column)
            new_column_name = column
        else:
            # If the column name is missing or is an integer, create a new column name prefix
            index_raw_columns += 1
            new_column_name = '{prefix}{index}'.format(prefix=generated_column_name_prefix,
                                                       index=index_raw_columns)

        new_column_names.append(new_column_name)
    return raw_feature_names, new_column_names


def get_feature_that_avoids_refitting(feature: Tuple[Union[str, List[str]], List[TransformerMixin], Dict[str, str]]) \
        -> Tuple[Union[str, List[str]], None, Dict[str, str]]:
    """
    Returns a copy of the provided feature that will cause fitting to be skipped. DataFrameMapper does this
    by default for features with a NoneType transformer list, so we will just be replacing that list.

    :param feature: The feature to be skipped.
    :return: A copy of the feature, modified to be skipped.
    """
    return feature[0], None, feature[2]
