# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Init file for azureml-explain-model/azureml/explain/model/common/model_wrapper."""
from interpret_community.common.model_wrapper import WrappedPytorchModel, WrappedClassificationModel, \
    WrappedRegressionModel

__all__ = ['WrappedPytorchModel', 'WrappedClassificationModel', 'WrappedRegressionModel']
