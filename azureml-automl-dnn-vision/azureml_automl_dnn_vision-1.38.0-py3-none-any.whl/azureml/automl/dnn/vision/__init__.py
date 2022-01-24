# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains code for automl dnn vision package."""

import sys
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared import log_server

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore[has-type]

# Mark this package as being allowed to log certain built-in types
module = sys.modules[__name__]
logging_utilities.mark_package_exceptions_as_loggable(module)
log_server.install_sockethandler('azureml.automl.dnn.vision')
