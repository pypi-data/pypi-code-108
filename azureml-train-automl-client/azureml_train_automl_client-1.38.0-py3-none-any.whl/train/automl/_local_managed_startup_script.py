# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core._logging import log_server
from azureml.automl.core.shared.exceptions import ManagedEnvironmentCorruptedException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import RuntimeModuleDependencyMissing
try:
    from azureml.train.automl.runtime._remote_script import local_managed_wrapper
    has_wrapper = True
except ImportError:
    has_wrapper = False

logger = logging.getLogger('azureml.train.automl._script')

if __name__ == '__main__':
    # Note: this file is not intended to be run manually, it is only used for submitting local managed runs
    with log_server.new_log_context():
        if has_wrapper:
            local_managed_wrapper()
        else:
            raise ManagedEnvironmentCorruptedException._with_error(
                AzureMLError.create(
                    RuntimeModuleDependencyMissing,
                    target="local-managed",
                    module_name="azureml-train-automl-runtime._remote_script.local_managed_wrapper"))
