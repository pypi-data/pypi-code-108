# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains functionality integrating Azure Machine Learning with MLFlow.

MLflow (https://mlflow.org/) is an open-source platform for tracking machine learning experiments and managing models.
You can use MLflow logging APIs with Azure Machine Learning so that the metrics and artifacts are logged to your Azure
machine learning workspace.

Within an Azure Machine Learning :class:`azureml.core.workspace`, add the code below to use MLflow. The
:meth:`azureml.core.workspace.Workspace.get_mlflow_tracking_uri` method sets the MLflow tracking URI to point
to your workspace.

    import mlflow
    from azureml.core import Workspace
    workspace = Workspace.from_config()
    mlflow.set_tracking_uri(workspace.get_mlflow_tracking_uri())

More examples can be found at https://aka.ms/azureml-mlflow-examples.
"""

import os
import logging
import re
from six.moves.urllib import parse


import azureml
from azureml.core import Workspace, Experiment, Run
from azureml.core.authentication import ArmTokenAuthentication

try:
    from azureml.mlflow._version import VERSION
except ImportError:
    VERSION = "0.0.0+dev"


_SUBSCRIPTIONS_PREFIX = "/subscriptions/"

logger = logging.getLogger(__name__)

__version__ = VERSION


def get_mlflow_tracking_uri(workspace):
    """
    Retrieve the tracking URI from Workspace for use in AzureMLflow.

    Return a URI identifying the workspace, with optionally the auth header
    embedded as a query string within the URI. The authentication header does not include the "Bearer " prefix.

    :return: Returns the URI pointing to this workspace, with the auth query paramter if with_auth is True.
    :rtype: str
    """
    from ._internal.service_context_loader import _AzureMLServiceContextLoader
    service_location = os.environ.get("AZUREML_DEV_URL_MLFLOW",
                                      parse.urlparse(workspace.service_context._get_mlflow_url()).netloc)
    workspace_scope = workspace.service_context._get_workspace_scope()
    logger.debug("Creating a tracking uri in {} for workspace {}".format(service_location, workspace_scope))

    store_uri = "azureml://{}/mlflow/v1.0{}{}".format(
        service_location,
        workspace_scope,
        "?")

    _AzureMLServiceContextLoader.add_service_context(store_uri, workspace.service_context)

    return store_uri


def _setup_remote(azureml_run):
    from azureml.mlflow._internal.constants import MLflowRunEnvVars
    logger.debug("Setting up a Remote MLflow run")
    tracking_uri = azureml_run.experiment.workspace.get_mlflow_tracking_uri() + "&is-remote=True"
    logger.debug("Setting MLflow tracking uri env var")
    os.environ[MLflowRunEnvVars.TRACKING_URI] = tracking_uri
    logger.debug("Setting MLflow run id env var with {}".format(azureml_run.id))
    os.environ[MLflowRunEnvVars.ID] = azureml_run.id
    logger.debug("Setting Mlflow experiment with {}".format(azureml_run.experiment.name))
    os.environ[MLflowRunEnvVars.EXPERIMENT_NAME] = azureml_run.experiment.name
    if azureml_run.experiment.id is not None:
        logger.debug("Setting Mlflow experiment with {}".format(azureml_run.experiment.id))
        os.environ[MLflowRunEnvVars.EXPERIMENT_ID] = azureml_run.experiment.id
    from mlflow.entities import SourceType

    if not os.environ.get("AZUREML_SECONDARY_INSTANCE"):
        mlflow_tags = {}
        mlflow_source_type_key = 'mlflow.source.type'
        if mlflow_source_type_key not in azureml_run.tags:
            logger.debug("Setting the mlflow tag {}".format(mlflow_source_type_key))
            mlflow_tags[mlflow_source_type_key] = SourceType.to_string(SourceType.JOB)
        mlflow_source_name_key = 'mlflow.source.name'
        if mlflow_source_name_key not in azureml_run.tags:
            logger.debug("Setting the mlflow tag {}".format(mlflow_source_name_key))
            mlflow_tags[mlflow_source_name_key] = azureml_run.get_details()['runDefinition']['script']
        azureml_run.set_tags(mlflow_tags)


def get_portal_url(run):
    """Get the URL to the Azure Machine Learning studio page for viewing run details.

    :param run: The run for which to view details.
    :type run: azureml.core.Run
    :return: A URL to the Azure Machine Learning studio which can be used to view
        run details, including run artifacts.
    :rtype: str
    """
    from ._internal.utils import get_aml_experiment_name, VERSION_WARNING
    from ._internal.store import AzureMLRestStore
    if isinstance(run, Run):
        return run.get_portal_url()
    else:
        from mlflow.tracking.client import MlflowClient
        experiment_name = MlflowClient().get_experiment(run.info.experiment_id).name
        run_id = run.info.run_id
        try:
            def_store = MlflowClient()._tracking_client.store
        except Exception:
            logger.warning(VERSION_WARNING.format("MlflowClient()._tracking_client.store"))
            def_store = MlflowClient().store
        aml_store = def_store if isinstance(def_store, AzureMLRestStore) else def_store.aml_store
        host = aml_store.get_host_creds().host
        netloc = aml_store.service_context._get_workspace_portal_url()
        uri = "{}{}".format(_SUBSCRIPTIONS_PREFIX, host.split(_SUBSCRIPTIONS_PREFIX, 2)[1])
        experiment_name = get_aml_experiment_name(experiment_name)
        experiment_run_uri = "/experiments/{}/runs/{}".format(experiment_name, run_id)
        return netloc + uri + experiment_run_uri


def _azureml_run_from_mlflow_run(mlflow_run):
    from ._internal.store import AzureMLRestStore
    from ._internal.utils import VERSION_WARNING
    from mlflow.tracking.client import MlflowClient
    experiment_name = MlflowClient().get_experiment(mlflow_run.info.experiment_id).name
    try:
        def_store = MlflowClient()._tracking_client.store
    except Exception:
        logger.warning(VERSION_WARNING.format("MlflowClient()._tracking_client.store"))
        def_store = MlflowClient().store
    aml_store = def_store if isinstance(def_store, AzureMLRestStore) else def_store.aml_store
    host = aml_store.get_host_creds().host
    auth_token = aml_store.get_host_creds().token

    cluster_url = host.split(_SUBSCRIPTIONS_PREFIX, 2)[0].split("/history/")[0]
    scope = "{}{}".format(_SUBSCRIPTIONS_PREFIX, host.split(_SUBSCRIPTIONS_PREFIX, 2)[1])
    auth = ArmTokenAuthentication(auth_token)
    run_id = mlflow_run.info.run_id

    subscription_id = re.search(r'/subscriptions/([^/]+)', scope).group(1)
    resource_group_name = re.search(r'/resourceGroups/([^/]+)', scope).group(1)
    workspace_name = re.search(r'/workspaces/([^/]+)', scope).group(1)
    workspace = Workspace(subscription_id,
                          resource_group_name,
                          workspace_name,
                          auth=auth,
                          _disable_service_check=True)

    experiment = Experiment(workspace, experiment_name)
    changed_env_var = False
    prev_env_var = None
    from azureml._base_sdk_common.service_discovery import HISTORY_SERVICE_ENDPOINT_KEY
    try:
        if HISTORY_SERVICE_ENDPOINT_KEY in os.environ:
            prev_env_var = os.environ[HISTORY_SERVICE_ENDPOINT_KEY]
        os.environ[HISTORY_SERVICE_ENDPOINT_KEY] = cluster_url
        changed_env_var = True
        azureml_run = Run(experiment, run_id)
        return azureml_run
    finally:
        if changed_env_var:
            if prev_env_var is not None:
                os.environ[HISTORY_SERVICE_ENDPOINT_KEY] = prev_env_var
            else:
                del os.environ[HISTORY_SERVICE_ENDPOINT_KEY]


def register_model(run, name, path, tags=None, **kwargs):
    """
    Register a model with the specified name and artifact path.

    .. remarks::

        .. code-block:: python

            model = register_model(run, 'best_model', 'outputs/model.pkl', tags={'my': 'tag'})

    :param name: The name to give the registered model.
    :type name: str
    :param path: The relative cloud path to the model, for example, "outputs/modelname".
    :type path: str
    :param tags: An optional dictionary of key value tags to pass to the model.
    :type tags: dict[str, str]
    :param kwargs: Optional parameters.
    :type kwargs: dict
    :return: A registered model.
    :rtype: azureml.core.model.Model
    """
    logger.warning("This method has been deprecated and will be removed in a future release. Please use "
                   "mlflow.register_model instead.")
    azureml_run = run if isinstance(run, Run) else _azureml_run_from_mlflow_run(run)
    return azureml_run.register_model(model_name=name, model_path=path, **kwargs)


if not hasattr(azureml.core.workspace.Workspace, "get_mlflow_tracking_uri"):
    # To replicate monkeypatched function for older SDKs
    logger.warning("Old Workspace definition detected, adding patched Workspace.get_mlflow_tracking_uri. "
                   "Please upgrade azureml-core.")
    azureml.core.workspace.Workspace.get_mlflow_tracking_uri = get_mlflow_tracking_uri

__all__ = ["get_portal_url", "register_model"]
