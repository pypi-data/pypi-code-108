# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Package containing modules used in automated machine learning.

Included classes provide resources for configuring, managing pipelines, and examining run output
for automated machine learning experiments.

For more information on automated machine learning, please see
https://docs.microsoft.com/azure/machine-learning/concept-automated-ml

To define a reusable machine learning workflow for automated machine learning, you may use
:class:`azureml.train.automl.AutoMLStep` to create a
:class:`azureml.pipeline.core.pipeline.Pipeline`.
"""
import sys
from azureml.automl.core.package_utilities import get_sdk_dependencies
from azureml.automl.core._logging import log_server
from azureml.automl.core.shared import logging_utilities

import warnings
with warnings.catch_warnings():
    # Suppress the warnings at the import phase.
    warnings.simplefilter("ignore")
    from azureml.train.automl.automlconfig import AutoMLConfig
    from azureml.train.automl.automlimageconfig import AutoMLImageConfig

try:
    from azureml.train.automl.runtime import AutoMLStep, AutoMLStepRun
    __all__ = [
        'AutoMLConfig',
        'AutoMLImageConfig',
        'get_sdk_dependencies',
        'AutoMLStep',
        'AutoMLStepRun']
except ImportError:
    __all__ = [
        'AutoMLConfig',
        'AutoMLImageConfig',
        'get_sdk_dependencies']

# TODO copy this file as part of setup in runtime package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)    # type: ignore

try:
    from ._version import ver as VERSION, selfver as SELFVERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    SELFVERSION = VERSION
    __version__ = VERSION

# Mark this package as being allowed to log certain built-in types
module = sys.modules[__name__]
logging_utilities.mark_package_exceptions_as_loggable(module)
log_server.install_handler('azureml.train.automl')
