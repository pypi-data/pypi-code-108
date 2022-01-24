# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains specialized functionality for working with Dataset objects in Azure Machine Learning."""

from azureml._base_sdk_common import __version__ as VERSION
from .labeled_dataset import Dataset, TabularDataset, FileHandlingOption, LabeledDatasetTask

__version__ = VERSION

__all__ = [
    'Dataset',
    'TabularDataset',
    'LabeledDatasetTask',
    'FileHandlingOption'
]
