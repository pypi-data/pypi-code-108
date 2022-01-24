# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Notebook generation code used to generate Jupyter notebooks from a Jinja2 template."""
from typing import Any, Callable, Mapping, Optional, Dict, Set, Tuple
import functools
import inspect
import json
import logging
import os
import pkg_resources

from . import utilities
from azureml._common._error_definition import AzureMLError
from azureml.core import Run
from azureml.core import Environment as AMLEnvironment
from azureml.core.compute import ComputeTarget
from azureml.core.compute_target import ComputeTargetException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared.exceptions import ClientException, ConfigException
from azureml.train.automl.runtime import __version__
from azureml.train.automl.runtime._code_generation.constants import CodeGenConstants

import jinja2
from jinja2 import Environment, meta


PACKAGE_NAME = 'azureml.train.automl.runtime'
logger = logging.getLogger(__name__)


class NotebookTemplate:
    """
    Generates notebooks using a Jupyter notebook template.
    """

    def __init__(self, notebook_template: str) -> None:
        """
        Create an instance of a NotebookGenerator.

        :param notebook_template: the Jupyter notebook to use as a template, as a string
        """
        self.template = notebook_template

    @functools.lru_cache(maxsize=1)
    def get_arguments(self) -> Set[str]:
        """
        Retrieve the names of all the arguments needed to generate the notebook.

        :return: a list of all argument names
        """
        notebook = json.loads(self.template)
        env = Environment()
        args = set()  # type: Set[str]

        # Parse the contents of each notebook cell into an AST and scan for jinja2 variables
        for cell in notebook.get("cells", []):
            source = cell.get("source")
            if source:
                if isinstance(source, str):
                    stringified_source = source
                else:
                    stringified_source = "".join(source)
                parsed = env.parse(stringified_source)
                args |= meta.find_undeclared_variables(parsed)
        return args

    def generate_notebook(self, notebook_args: Dict[str, Any]) -> str:
        """
        Generate a notebook from a template using the provided arguments.

        :param notebook_args: a dictionary containing keyword arguments
        :return: a Jupyter notebook as a string
        """
        required_args = self.get_arguments()
        provided_args = set(notebook_args)
        missing_args = required_args - provided_args
        extra_args = provided_args - required_args

        logger.info("Unused arguments: {}".format(extra_args))

        if any(missing_args):
            raise ClientException._with_error(
                AzureMLError.create(
                    AutoMLInternal,
                    target="generate_notebook",
                    error_details="Mismatch between template and provided arguments. Missing arguments: {}".format(
                        missing_args
                    ),
                )
            )

        # Render the notebook template using the given arguments.
        # Arguments need to be escaped since Jupyter notebooks are in JSON format.
        env = Environment(undefined=jinja2.StrictUndefined)
        template = env.from_string(self.template)
        source = template.render(**{k: self.escape_json(notebook_args[k]) for k in notebook_args})

        # Tag the notebook with the SDK version used to generate it.
        node = json.loads(source)
        if "metadata" not in node:
            node["metadata"] = {}
        node["metadata"]["automl_sdk_version"] = __version__

        return json.dumps(node)

    @staticmethod
    def escape_json(input_str: Any) -> Any:
        """
        JSON escape a string. Other types are unaffected.

        :param input_str: the string
        :return: an escaped string, or original object if not a string
        """
        if not isinstance(input_str, str):
            return input_str
        return json.dumps(input_str).replace('/', r'\/')[1:-1]


def get_template(notebook_name: str) -> NotebookTemplate:
    """
    Load a notebook template from this package using its filename w/o extension.

    :param notebook_name:
    :return:
    """
    logger.info('Loading notebook {}'.format(notebook_name))
    template_path = pkg_resources.resource_filename(
        PACKAGE_NAME,
        os.path.join('_code_generation', 'notebook_templates', notebook_name + '.ipynb.template')
    )
    with open(template_path, 'r') as f:
        return NotebookTemplate(f.read())


def remove_matching_default_args(func: Callable[..., Any], args: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Given a function and function arguments, remove any arguments that match defaults in the function signature.

    :param func:
    :param args:
    :return:
    """
    signature = inspect.signature(func)

    # Ger all the default arguments from the function
    default_args = {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

    # Only pick arguments if they either do not match a default argument or are not in the default argument list
    new_args = {
        k: v
        for k, v in args.items()
        if k not in default_args or v != default_args[k]
    }
    return new_args


def generate_script_run_notebook(
        automl_child_run: Run,
        version: Optional[str] = None,
        extra_index: Optional[str] = None,
        environment: Optional[AMLEnvironment] = None
) -> str:
    # TODO: Export _environment_utilities.modify_run_configuration() like functionality in the notebook to ensure
    # all required packages are installed
    template_name = "script_run"
    template = get_template(template_name)
    logger.info('Notebook arguments: {}'.format(template.get_arguments()))

    # Leaving this for reference on how to get the extra index URL for a package version.
    # This is only needed if SDK doesn't know where the origin of the current version is and we need to override it
    # extra_index = CondaDependencies.sdk_origin_url().rstrip("/")
    # extra_index = extra_index if extra_index != PYPI_INDEX else None

    environment_name = environment.name if environment else None
    environment_version = environment.version if environment else None

    parent_run = automl_child_run.parent
    experiment = parent_run.experiment
    workspace = experiment.workspace

    training_dataset_id, validation_dataset_id = utilities.get_input_datasets(parent_run)

    properties = parent_run.properties
    compute_target_name = properties.get("compute_target")
    if not isinstance(compute_target_name, str):
        compute_target_name = "cpu-cluster"
    try:
        compute_target = ComputeTarget(workspace=workspace, name=compute_target_name)
        compute_sku = compute_target.vm_size
    except ComputeTargetException:
        compute_sku = CodeGenConstants.DefaultComputeSku

    notebook = template.generate_notebook({
        'experiment_name': experiment.name,
        'workspace_name': workspace._workspace_name,
        'resource_group': workspace._resource_group,
        'subscription_id': workspace._subscription_id,
        'training_package': "azureml-train-automl~={}".format(version or __version__),
        'script_filename': CodeGenConstants.ScriptFilename,
        'extra_index_url': extra_index,
        'environment_name': environment_name,
        'environment_version': environment_version,
        'automl_child_run_id': automl_child_run.id,
        'compute_target': compute_target_name,
        'training_dataset_id': training_dataset_id,
        'validation_dataset_id': validation_dataset_id,
        'compute_sku': compute_sku
    })
    return notebook
