# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/common/metrics."""
from interpret_community.common.metrics import dcg, ndcg

__all__ = ['dcg', 'ndcg']
