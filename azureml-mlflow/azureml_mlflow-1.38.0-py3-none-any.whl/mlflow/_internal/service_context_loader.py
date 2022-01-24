# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os

from six.moves.urllib import parse

from azureml.core import Run
from azureml.exceptions import RunEnvironmentException

from azureml._run_impl.constants import RunEnvVars

from .utils import (get_service_context_from_tracking_url_default_auth,
                    get_service_context_from_tracking_url_mlflow_env_vars,
                    _IS_REMOTE,
                    _TRUE_QUERY_VALUE)

logger = logging.getLogger(__name__)


def _mlflow_env_vars_set():
    return ("MLFLOW_TRACKING_URI" in os.environ
            and "MLFLOW_TRACKING_TOKEN" in os.environ and "MLFLOW_RUN_ID" in os.environ
            and ("MLFLOW_EXPERIMENT_ID" in os.environ or "MLFLOW_EXPERIMENT_NAME" in os.environ))


def _is_remote():
    return RunEnvVars.ID in os.environ or "MLFLOW_RUN_ID" in os.environ


class _AzureMLServiceContextLoader(object):
    """
    _AzureMLStoreLoader loads an AzureMLStore from 3 supported scenarios.

    1, new tracking_uri without is remote set to True. A store is created from the uri
    2, is remote set to true in a workspace tracking uri. Loads the
       store information from the current Run context and sets the experiment and ActiveRun.
    3, a cached result of option 1 or 2, this cache is relative to the netloc + path of the tracking_uri
    """

    _tracking_uri_to_service_context = {}

    @classmethod
    def has_service_context(cls, store_uri):
        cache_key = store_uri.split("?")[0]
        return cache_key in cls._tracking_uri_to_service_context

    @classmethod
    def add_service_context(cls, store_uri, service_context):
        cache_key = store_uri.split("?")[0]
        cls._tracking_uri_to_service_context[cache_key] = service_context

    @classmethod
    def get_service_context(cls, store_uri):
        cache_key = store_uri.split("?")[0]
        return cls._tracking_uri_to_service_context[cache_key]

    @classmethod
    def load_service_context(cls, store_uri):
        from mlflow.exceptions import MlflowException

        parsed_url = parse.urlparse(store_uri)
        queries = dict(parse.parse_qsl(parsed_url.query))

        cache_key = store_uri.split("?")[0]

        if cls.has_service_context(cache_key):
            return cls.get_service_context(cache_key)

        elif _mlflow_env_vars_set():
            service_context = get_service_context_from_tracking_url_mlflow_env_vars(parsed_url)
            logger.debug(
                "Created a new service context from mlflow env vars: {}".format(service_context))
            cls.add_service_context(cache_key, service_context)

        elif _IS_REMOTE in queries and queries[_IS_REMOTE] == _TRUE_QUERY_VALUE:
            try:
                run = Run.get_context()
            except RunEnvironmentException:
                raise MlflowException(
                    "AzureMlflow tracking URI was set to remote but there "
                    "was a failure in loading the run.")
            else:
                service_context = run.experiment.workspace.service_context
                cls.add_service_context(cache_key, service_context)
                logger.debug("Found Run's service context: {}".format(service_context))

        else:
            if _is_remote():
                raise MlflowException(
                    "In remote environment but could not load a service "
                    "context. InteractiveLoginAuthentication is not supported in "
                    "the remote environment.")
            else:
                service_context = get_service_context_from_tracking_url_default_auth(parsed_url)
                logger.debug("Creating a new {} for a local run".format(service_context))
                cls.add_service_context(cache_key, service_context)

        return cls.get_service_context(cache_key)
