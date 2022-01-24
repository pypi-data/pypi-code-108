# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains core automated machine learning classes for Azure Machine Learning.
This package is used by azureml-train-automl-client and azureml-train-automl-runtime.
"""
import os
import sys

from ._shared_package_legacy_import import handle_legacy_shared_package_imports
from .shared import logging_utilities
from ._logging import log_server


__all__ = []

# TODO copy this file as part of setup in runtime package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)    # type: ignore

# Make the 'shared' package importable through its legacy aliases.
handle_legacy_shared_package_imports()

try:
    from ._version import ver as VERSION, selfver as SELFVERSION
    __version__ = VERSION
except ImportError:
    VERSION = '0.0.0+dev'
    SELFVERSION = VERSION
    __version__ = VERSION

module = sys.modules[__name__]
logging_utilities.mark_package_exceptions_as_loggable(module)

log_server.install_handler('azureml.automl.core')
log_server.install_handler('automl.client.core.common')
