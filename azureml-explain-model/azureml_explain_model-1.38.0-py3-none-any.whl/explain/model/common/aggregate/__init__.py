# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/common/aggregate."""
from interpret_community.common.aggregate import init_aggregator_decorator, add_explain_global_method

__all__ = ['init_aggregator_decorator', 'add_explain_global_method']
