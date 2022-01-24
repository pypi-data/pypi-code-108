# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class for handling notebook run configuration."""

import os
import json


def _insert_suffix(filename, suffix="output"):
    base = os.path.splitext(filename)
    return base[0] + ".output" + base[1]


class NotebookExecutionHandler:
    """Represents the base class for notebook execution handlers.

    :param handler_script: The Python script name to execute a notebook.
    :type handler_script: str
    :param dependencies: A list of pip dependencies.
    :type dependencies: list
    """

    def _argument_handling_contract(self, notebook, output_notebook, parameters=None):
        """Return list of arguments in handler accepted format.

        :param notebook: The input notebook.
        :type notebook: str
        :param output_notebook: The output notebook.
        :type output_notebook: str
        :param parameters: A dictionary of parameters.
        :type parameters: dict

        :return: List of parameters.
        :rtype: list
        """
        return ["-i", notebook,
                "-o", output_notebook if output_notebook else _insert_suffix(notebook),
                "-p", json.dumps(parameters)]

    def __init__(self, handler_script, dependencies=None):
        """Construct NotebookExecutionHandler object.

        :param handler_script: The Python script name to execute a notebook.
        :type handler_script: str
        :param dependencies: A list of pip dependencies.
        :type dependencies: list
        """
        self._script_source = handler_script
        self.script = os.path.basename(handler_script)
        # Dependencies for the handler only. Notebook dependencies must be added into a run config
        self.dependencies = dependencies if dependencies else []
