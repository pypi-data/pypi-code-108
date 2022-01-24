# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for Column purpose detection."""

from typing import List

from azureml.automl.runtime.column_purpose_detection import StatsAndColumnPurposeType


def get_column_purposes_user_friendly(stats_and_column_purposes: List[StatsAndColumnPurposeType]) -> List[str]:
    column_drop_reason_list = []  # type: List[str]
    for _, column_purpose, column_name in stats_and_column_purposes:
        column_drop_reason_list.append(
            "Column {} identified as {}.".format(column_name, column_purpose)
        )
    return column_drop_reason_list
