# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/common/progress."""
from interpret_community.common.structured_model_explainer import StructuredInitModelExplainer, \
    PureStructuredModelExplainer

__all__ = ['StructuredInitModelExplainer', 'PureStructuredModelExplainer']
