# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for validations which require interacting with AzureML."""

import logging

from azureml.core.model import Model

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)

_MODEL_ID_SPLIT_CHAR = ':'

_MODEL_ERROR = "Models"
_MODEL_ID_NO_SPLIT = "Could not split '{0}' into name and version"
_MODEL_NAME_NOT_EXIST = "'{0}' does not exist in the workspace"
_MODEL_VERSION_NOT_EXIST = "'{0}' has no version {1}"


def _build_message(fmt, *args):
    """Format an exception message."""
    mesg = fmt.format(*args)

    return "{0}: {1}".format(_MODEL_ERROR, mesg)


def validate_models_exist(workspace, model_ids):
    """Verify that the given list of model ids all exist in the workspace

    To facilitate linking of AzureML entities, we can require that all
    the entries in the `modelNames` list supplied to the dashboard be
    valid values of `Model.id `in the current workspace. Note that the
    `Model.id` is actually a string "`<name>:<version>`" and not a GUID.

    :param workspace: The workspace to be checked
    :type workspace: "class:`azureml.core.workspace.Workspace`
    :param model_ids: The list of model ids to be checked
    :type model_ids: list(str)
    """
    _logger.info("Validating model ids exist")
    for model_id in model_ids:
        _logger.info("Checking {0}".format(model_id))
        # The constructor for Model checks with the service and will throw
        # an exception if the specified Model doesn't exist
        Model(workspace, id=model_id)
    _logger.info("Validation of model ids complete")
