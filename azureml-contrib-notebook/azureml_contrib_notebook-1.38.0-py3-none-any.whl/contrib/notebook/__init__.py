# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains extensions for working with Jupyter notebooks in Azure Machine Learning.

With this package you can capture notebooks on runs, use Papermill to parameterize and execute notebooks,
and run a local notebook as a pipeline step.
"""
from azureml.contrib.notebook.extension import Extension, load_ipython_extension
from azureml.contrib.notebook._notebook_handler import NotebookExecutionHandler
from azureml.contrib.notebook._notebook_run_config import NotebookRunConfig
from azureml.contrib.notebook._papermill_deprecated_handler import PapermillExecutionHandler
from azureml.contrib.notebook._azureml_handler import AzureMLNotebookHandler
from azureml.contrib.notebook._azureml_appinsights_handler import AzureMLApplicationInsightsNotebookHandler
from azureml.contrib.notebook._notebook_runner_step import NotebookRunnerStep

__all__ = [
    "AzureMLApplicationInsightsNotebookHandler",
    "AzureMLNotebookHandler",
    "Extension",
    "load_ipython_extension",
    "NotebookExecutionHandler",
    "NotebookRunConfig",
    "NotebookRunnerStep",
    "PapermillExecutionHandler"
]


def _jupyter_server_extension_paths():
    return [{
        "module": "notebook"
    }]


# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="_scripts",
        dest="azureml",
        require="azureml/kernel")]
