# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Convenience names for long types."""
from typing import Tuple

from azureml.automl.runtime.stats_computation import RawFeatureStats

# Stats and column purposes type containing RawFeatureStats, ColumnPurpose, Column
# TODO: Make this a proper class!
StatsAndColumnPurposeType = Tuple[RawFeatureStats, str, str]
