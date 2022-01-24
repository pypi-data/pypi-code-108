# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Suggest featurizers API module."""

from .dynamic_suggestions import perform_feature_sweeping
from ._suggest_featurizers import suggest_featurizers
from .suggest_featurizers_timeseries import (
    suggest_featurizers_timeseries,
    _is_short_grain_handled,
    _should_remove_lag_lead_and_rw
)
