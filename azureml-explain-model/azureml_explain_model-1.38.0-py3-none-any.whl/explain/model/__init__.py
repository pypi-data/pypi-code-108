# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for model interpretability, including feature and class importance for blackbox and whitebox models.

You can use model interpretability to explain why a model model makes the predictions it does and help build
confidence in the model.  For more information, see the article
https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability.
"""

import warnings

from .tabular_explainer import TabularExplainer


warnings.warn("The azureml-explain-model package is deprecated and will be removed in a future release "
              "of the AzureML SDK. Please use the azureml-interpret and interpret-community packages "
              "which support the functionality azureml-explain-model used to provide.")

__all__ = ["TabularExplainer"]
