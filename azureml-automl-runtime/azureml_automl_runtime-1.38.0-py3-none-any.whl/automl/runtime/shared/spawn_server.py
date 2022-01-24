# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functionality to execute a function in a child process created using "spawn".

This file contains the server portion.
"""
import dill
import logging
import sys

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory
from azureml.automl.core._logging import log_server
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.fake_traceback import FakeTraceback
from azureml.automl.core.shared.exceptions import ResourceException

logger = logging.getLogger("azureml.automl.runtime.shared.spawn_server")


def run_server(config_file_name, input_file_name, output_file_name, error_file_name):
    """Run the server."""
    # Pre-allocate a memory error just in case
    ex = ResourceException._with_error(AzureMLError.create(InsufficientMemory))

    error = ex, FakeTraceback.serialize_exception_tb(ex)
    with open(error_file_name, "wb") as f:
        dill.dump(error, f, protocol=dill.HIGHEST_PROTOCOL)

    try:
        # Deserialize the configuration object using dill.
        with open(config_file_name, "rb") as f:
            config = dill.load(f)

        # Initialize system path to match parent process configuration.
        sys.path = config["path"]

        # Deserialize the input file using dill.
        with open(input_file_name, "rb") as f:
            obj = dill.load(f)

        for logger_name in config["logger_names"]:
            log_server.install_handler(logger_name)

        with log_server.lock:
            # Set verbosity after loading function, since deserialization can cause dependencies to set the log level.
            log_server.set_verbosity(config["log_verbosity"])
            log_server.custom_dimensions.update(config["custom_dimensions"])

        # Deconstruct the input into function, arguments, keywords arguments.
        fn, args, kwargs = obj

        # run_server typically is run on in the context of a subprocess. The only state that is maintained across the
        # process boundary is pickled via args & kwargs. In order to ensure the ExperimentStore is correctly set
        # we must reset the singleton.
        # Task 1202099 - remove AutoML specific code from resource limits and spawn proc.
        if "cache_store" in kwargs:
            # We only need to recreate the ExperimentStore instance in cases where cache_store is an argument to the
            # spawn_server.
            from azureml.automl.runtime.experiment_store import ExperimentStore
            cache_store = kwargs.pop("cache_store")
            expr_store = ExperimentStore(cache_store, read_only=True)
            expr_store.load()

        # Invoke the function and store the result in a (value, error) pair.
        # TODO: Currently this code assumes that the called function will already return such a pair. Need to fix.
        ret, ex = fn(*args, **kwargs)

        # Write the result to the output file using dill.
        # HIGHEST_PROTOCOL is needed for models greater than 4Gb
        with open(output_file_name, "wb") as f:
            dill.dump(ret, f, protocol=dill.HIGHEST_PROTOCOL)
    except BaseException as e:
        ret = None
        ex = e

    # The following is not guaranteed to succeed if we're out of memory, which is why we wrote the memory error to
    # the file earlier.
    try:
        if ex is not None:
            logging_utilities.log_traceback(ex, logger)

        error = ex, FakeTraceback.serialize_exception_tb(ex)
        error_serialized = dill.dumps(error, protocol=dill.HIGHEST_PROTOCOL)
        with open(error_file_name, "wb") as f:
            f.write(error_serialized)
    except (dill.PicklingError, MemoryError):
        # The prewritten memory error should be sufficient here.
        pass


if __name__ == "__main__":
    # Check command-line arguments.
    if len(sys.argv) != 5:
        print("Usage: spawn_server config_file input_file output_file error_file")
        exit(10)

    # Extract configuration, input, and output file names.
    config_file_name = sys.argv[1]
    input_file_name = sys.argv[2]
    output_file_name = sys.argv[3]
    error_file_name = sys.argv[4]

    try:
        run_server(config_file_name, input_file_name, output_file_name, error_file_name)
    except Exception as e:
        sys.stderr.write("{}\n".format(e))
        logging_utilities.log_traceback(e, logger)
        exit(20)
