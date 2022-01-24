# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for packaging Azure Machine Learning models for deployment to Azure Functions.

Azure Functions allows you to run small pieces of code (called "functions") that can be triggered by a
specified event, such as changes in  data, or on a schedule as often needed in machine learning workflows.
For more information, see [An introduction to Azure Functions](https://docs.microsoft.com/azure/azure-functions/).

With the functions in this package, you can create Azure Functions applications from models registered
in your Azure Machine Learning workspace. Each function returns a :class:`azureml.core.model.ModelPackage`
object representing either a Docker image that encapsulates your model and its dependencies or a
Dockerfile build context.

For examples of using Azure Functions for machine learning, see [Tutorial: Apply machine learning models
in Azure Functions with Python and
TensorFlow](https://docs.microsoft.com/azure/azure-functions/functions-machine-learning-tensorflow) and
[Tutorial: Deploy a pre-trained image classification model to Azure Functions with
PyTorch](https://docs.microsoft.com/azure/azure-functions/machine-learning-pytorch).
"""

from ._package import SERVICE_BUS_QUEUE_TRIGGER, BLOB_TRIGGER, HTTP_TRIGGER, package, package_http, package_blob, \
    package_service_bus_queue
from azureml.core import VERSION

__version__ = VERSION

__all__ = [
    "SERVICE_BUS_QUEUE_TRIGGER",
    "BLOB_TRIGGER",
    "HTTP_TRIGGER",
    "package",
    "package_http",
    "package_blob",
    "package_service_bus_queue"
]
