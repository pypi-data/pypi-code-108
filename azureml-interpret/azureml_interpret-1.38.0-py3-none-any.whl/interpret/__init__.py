# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for working with model interpretability in Azure Machine Learning.

You can use model interpretability to explain why a model makes the predictions it does and help build confidence
in the model. With this package you can get feature and class importance for blackbox and whitebox models, on both
raw and engineered features. For more information, see the article [Model interpretability in Azure Machine
Learning](https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability).

This package uses the interpretability techniques developed in the
[Interpret Community SDK](https://github.com/interpretml/interpret-community), an open source Python package for
training interpretable models and helping to explain blackbox systems, with additional interpretability techniques
and utility functions to handle real-world datasets and workflows. The Interpret Community SDK hosts the Azure
Machine Learning SDK supported explainers such as SHAP explainers, Mimic Explainer, Tabular Explainer, and others.

The key class in this package is the :class:`azureml.interpret.MimicWrapper` class, which provides a wrapper
to reduce the number of function calls needed to work with the interpret model package.
"""

from ._internal.explanation_client import ExplanationClient
from .mimic_wrapper import MimicWrapper

__all__ = ['ExplanationClient', 'MimicWrapper']
