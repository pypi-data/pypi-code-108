# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for running automated ML in pipelines, working with model explainers, and creating ensembles.

Included in this package are classes for configuring and managing pipelines, and examining run output
for automated machine learning experiments. For more information about automated machine learning in Azure,
see the article [What is automated machine
learning?](https://docs.microsoft.com/azure/machine-learning/concept-automated-ml)

To define a reusable machine learning workflow for automated machine learning, use
:class:`azureml.train.automl.runtime.AutoMLStep` to create a
:class:`azureml.pipeline.core.pipeline.Pipeline`.
"""
import warnings
with warnings.catch_warnings():
    # Suppress the warnings at the import phase.
    warnings.simplefilter("ignore")
    from .automl_step import AutoMLStep, AutoMLStepRun

__all__ = [
    'AutoMLStep',
    'AutoMLStepRun']

try:
    from ._version import ver as VERSION, selfver as SELFVERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    SELFVERSION = VERSION
    __version__ = VERSION
