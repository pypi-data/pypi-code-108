# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines constants used by the ExplanationClient."""

from azureml.interpret.common.constants import (
    ExplainParams, History)

FALSE = 'False'
# Limit local importance size to 10 MB
LOCAL_IMP_SIZE_LIMIT = 10000000
TRUE = 'True'
U_EVAL = '_eval'
U_EVAL_DATA = '_' + ExplainParams.EVAL_DATA
U_LOCAL_IMPORTANCE_VALUES = '_' + ExplainParams.LOCAL_IMPORTANCE_VALUES
U_YS_PRED = '_' + History.YS_PRED
U_YS_PRED_PROBA = '_' + History.YS_PRED_PROBA
