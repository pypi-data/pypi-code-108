# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/common/policy."""
from interpret_community.common.policy import SamplingPolicy
from azureml.explain.model.common.storage_policy import storage_policy

__all__ = ['SamplingPolicy', 'storage_policy']
