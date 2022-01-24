# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**AzureMLTrackingStore** provides a base class for MLFlow RestStore related handling."""

import logging
import time
from abc import ABCMeta

from mlflow.exceptions import RestException
from mlflow.utils.rest_utils import MlflowHostCreds

from azureml._restclient.clientbase import DEFAULT_BACKOFF, DEFAULT_RETRIES, execute_func
from azureml._restclient.workspace_client import WorkspaceClient


_AUTHORIZATION_PREFIX_LENGTH = len("Bearer ")  # Auth tokens are returned as Bearer <token>

logger = logging.getLogger(__name__)


class AzureMLAbstractRestStore(object):
    """
    Client for a remote rest server accessed via REST API calls.

    :param service_context: Service context for the AzureML workspace
    :type service_context: azureml._restclient.service_context.ServiceContext
    """
    __metaclass__ = ABCMeta

    def __init__(self, service_context, host_creds=None):
        """
        Construct an AzureMLRestStore object.

        :param service_context: Service context for the AzureML workspace
        :type service_context: azureml._restclient.service_context.ServiceContext
        """
        self.service_context = service_context
        self.get_host_creds = host_creds if host_creds is not None else self.get_host_credentials
        self.workspace_client = WorkspaceClient(service_context)

    def get_host_credentials(self):
        """
        Construct a MlflowHostCreds to be used for obtaining fresh credentials and the host url.

        :return: The host and credential for rest calls.
        :rtype: mlflow.utils.rest_utils.MlflowHostCreds
        """
        url_base = self.service_context._get_mlflow_url() + "/mlflow/v1.0"
        auth_header = self.service_context.get_auth().get_authentication_header()
        return MlflowHostCreds(url_base + self.service_context._get_workspace_scope(),
                               token=auth_header["Authorization"][_AUTHORIZATION_PREFIX_LENGTH:])

    @classmethod
    def _call_endpoint_with_retries(cls, rest_store_call_endpoint, *args, **kwargs):
        total_retry = DEFAULT_RETRIES
        backoff = DEFAULT_BACKOFF
        for i in range(total_retry):
            try:
                return execute_func(rest_store_call_endpoint, *args, **kwargs)
            except RestException as rest_exception:
                more_retries_left = i < total_retry - 1
                is_throttled = rest_exception.json.get("error", {"code": 0}).get("code") == "RequestThrottled"
                if more_retries_left and is_throttled:
                    logger.debug("There were too many requests. Try again soon.")
                    cls._wait_for_retry(backoff, i, total_retry)
                else:
                    raise

    def _call_endpoint(self, *args, **kwargs):
        return self._call_endpoint_with_retries(super(AzureMLAbstractRestStore, self)._call_endpoint, *args, **kwargs)

    @classmethod
    def _wait_for_retry(cls, back_off, left_retry, total_retry):
        delay = back_off * 2 ** (total_retry - left_retry - 1)
        time.sleep(delay)
