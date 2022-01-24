# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""This package contains functionality for creating a Windows compute target in Azure Machine Learning.

Windows-based compute targets enable running training or simulation tasks that can only be run, or are more
convenient to run, on a Windows-based system.

For more information about choosing compute targets for training and deployment, see [What are compute targets in
Azure Machine Learning?](https://docs.microsoft.com/azure/machine-learning/concept-compute-target)
"""

from ._amlWindowsCompute import AmlWindowsCompute, AmlWindowsComputeProvisioningConfiguration, AmlWindowsComputeStatus
from azureml._base_sdk_common import __version__ as VERSION

__version__ = VERSION

__all__ = [
    "AmlWindowsCompute",
    "AmlWindowsComputeProvisioningConfiguration",
    "AmlWindowsComputeStatus"
]
