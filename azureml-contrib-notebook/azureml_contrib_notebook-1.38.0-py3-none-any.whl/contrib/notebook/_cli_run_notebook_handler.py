# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os

from azureml.contrib.notebook._notebook_handler import NotebookExecutionHandler, _insert_suffix


class CLIRunNotebookHandler(NotebookExecutionHandler):
    """Notebook execution handler for CLI runs.

    :param history: Enable metrics logs to run history. Enabled by default.
    :type history: bool
    :param timeout: Cell execution timeout in seconds.
    :type timeout: int
    :param papermill_args: Dictionary of optional parameters to Papermill. See `:attr:supported_options` and
        https://papermill.readthedocs.io/en/latest/usage-cli.html for available options.
    :type papermill_args: dict
    :param output_directory: Directory in run artifacts for output notebooks.
    :type output_directory: str
    :param glob_inputs: Expand input notebook paths as glob patterns.
    :type glob_inputs: bool
    :param child_runs: Number of child runs to create for running notebooks.
    :type child_runs: int
    :param processes: Number of parallel processes to use for running notebooks within each run.
    :type processes: str
    """

    supported_options = [
        "progress_bar",
        "log_output",
        "kernel_name",
        "cwd"
    ]

    def __init__(self, history=True, timeout=None, papermill_args=None, output_directory=None,
                 glob_inputs=False, child_runs=None, processes=None):
        """Construct CLIRunNotebookHandler object."""
        super().__init__(os.path.join(os.path.dirname(__file__), "_handlers", "cli_run_notebook_script.py"),
                         ["azureml-contrib-notebook[full]"])

        if not papermill_args:
            papermill_args = {}

        for key, val in papermill_args.items():
            if key not in self.supported_options:
                raise Exception("Unsupported option: {}".format(key))

        papermill_args["engine_name"] = "azureml_engine"

        self.execution_args = {"history": history, "timeout": timeout}
        self.papermill_args = papermill_args or {}

        self.output_directory = output_directory
        self.glob_inputs = glob_inputs
        self.child_runs = child_runs
        self.processes = processes

    def _argument_handling_contract(self, notebook, output_notebook, parameters=None):
        """Return list of arguments in handler accepted format.

        :param notebook: Input notebook(s)
        :type path: str or list[str]
        :param output_notebook: Output notebook
        :type path: str
        :param parameters: Dictionary of parameters
        :type path: dict
        :param output_directory: Output notebook directory
        :type output_directory: str

        :return: List of parameters.
        :rtype: list
        """
        args = []

        if isinstance(notebook, list):
            for path in notebook:
                args += ["-i", path]
        else:
            args += ["-i", notebook]

        output_directory = self.output_directory

        if not (output_notebook or output_directory):
            if isinstance(notebook, list):
                output_directory = "outputs"
            else:
                output_notebook = _insert_suffix(notebook)

        if output_notebook:
            args += ["-o", output_notebook]
        else:
            args += ["-d", output_directory]

        if self.glob_inputs:
            args += ["--glob-input-paths"]

        if self.child_runs:
            args += ["--child-runs", self.child_runs]

        if self.processes is not None:
            args += ["--processes", str(self.processes)]

        args += ["-e", json.dumps(self.execution_args)]
        args += ["-p", json.dumps(self.papermill_args)]
        args += ["-n", json.dumps(parameters)]

        return args
