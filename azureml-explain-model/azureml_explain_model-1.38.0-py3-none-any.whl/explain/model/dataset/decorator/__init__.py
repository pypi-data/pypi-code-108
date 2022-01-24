# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/dataset/decorator."""
from interpret_community.dataset.decorator import tabular_decorator, init_tabular_decorator

__all__ = ['tabular_decorator', 'init_tabular_decorator']
