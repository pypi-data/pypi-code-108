# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**AzureMLflowStore** provides a class to read and record run metrics and artifacts on Azure via MLflow."""

import logging
import os

from functools import wraps
from six.moves.urllib import parse

import mlflow
from mlflow.utils.rest_utils import MlflowHostCreds
from mlflow.entities import ViewType

from azureml._run_impl.constants import RunEnvVars

from .utils import (execute_func, handle_exception, get_aml_experiment_name,
                    tracking_uri_decomp, _SUB_ID, _RES_GRP, _WS_NAME, VERSION_WARNING)

from .authentication import DBTokenAuthentication
from .hybrid_service_context import HybridServiceContext
from .azureml_reststore import AzureMLAbstractRestStore


logger = logging.getLogger(__name__)

try:
    from mlflow.store.tracking.rest_store import RestStore
    from mlflow.store.tracking import SEARCH_MAX_RESULTS_DEFAULT
except ImportError:
    logger.warning(VERSION_WARNING.format("from mlflow"))
    from mlflow.store.rest_store import RestStore
    from mlflow.store import SEARCH_MAX_RESULTS_DEFAULT

PARAM_PREFIX = "azureml.param."

_EXPERIMENT_NAME_ENV_VAR = "MLFLOW_EXPERIMENT_NAME"
_MLFLOW_RUN_ID_ENV_VAR = "MLFLOW_RUN_ID"


class AzureMLRestStore(AzureMLAbstractRestStore, RestStore):
    """
    Client for a remote tracking server accessed via REST API calls.

    :param service_context: Service context for the AzureML workspace
    :type service_context: azureml._restclient.service_context.ServiceContext
    """

    def __init__(self, service_context, host_creds=None, **kwargs):
        """
        Construct an AzureMLRestStore object.

        :param service_context: Service context for the AzureML workspace
        :type service_context: azureml._restclient.service_context.ServiceContext
        """
        logger.debug("Initializing the AzureMLRestStore")
        AzureMLAbstractRestStore.__init__(self, service_context, host_creds)
        RestStore.__init__(self, self.get_host_creds, **kwargs)

    @wraps(RestStore.update_run_info)
    def update_run_info(self, run_id, *args, **kwargs):
        remote_run_id = os.environ.get(RunEnvVars.ID)
        if remote_run_id is not None and run_id == remote_run_id:
            logger.debug("Status update was skipped for remote run {}".format(run_id))
            return self.get_run(run_id).info
        return super(AzureMLRestStore, self).update_run_info(run_id, *args, **kwargs)


class AdbAzuremlRestStore(RestStore):

    def __init__(self, tracking_uri):
        """Construct an AdbAzuremlRestStore object."""
        self._tracking_uri = tracking_uri

        self.adb_store = self.get_db_store()
        self.aml_store = self.get_aml_store()
        self.stores = [self.adb_store, self.aml_store]
        self.reader_store = self.stores[0]
        self.get_host_creds = self.get_host_credentials
        super(AdbAzuremlRestStore, self).__init__(self.get_host_creds)

    def get_db_store(self):
        try:
            tracking_uri = mlflow.get_tracking_uri()
        except ImportError:
            logger.warning(VERSION_WARNING.format("mlflow.get_tracking_uri"))
            tracking_uri = mlflow.tracking.get_tracking_uri()

        from mlflow.utils.databricks_utils import get_databricks_host_creds
        try:
            # If get_db_info_from_uri exists, it means mlflow 1.10 or above
            from mlflow.utils.uri import get_db_info_from_uri
            profile, path = get_db_info_from_uri("databricks")

            return RestStore(lambda: get_databricks_host_creds(tracking_uri))
        except ImportError:
            try:
                from mlflow.utils.uri import get_db_profile_from_uri
            except ImportError:
                logger.warning(VERSION_WARNING.format("from mlflow"))
                from mlflow.tracking.utils import get_db_profile_from_uri

            profile = get_db_profile_from_uri("databricks")
            logger.info("tracking uri: {} and profile: {}".format(tracking_uri, profile))
            return RestStore(lambda: get_databricks_host_creds(profile))

    def get_aml_store(self):
        try:
            tracking_uri = mlflow.get_tracking_uri()
        except ImportError:
            logger.warning(VERSION_WARNING.format("mlflow.get_tracking_uri"))
            tracking_uri = mlflow.tracking.get_tracking_uri()
        logger.info("tracking uri: {}".format(tracking_uri))
        parsed_url = parse.urlparse(tracking_uri)
        region = parsed_url.netloc
        parsed_path = tracking_uri_decomp(parsed_url.path)
        subscription_id = parsed_path[_SUB_ID]
        resource_group_name = parsed_path[_RES_GRP]
        workspace_name = parsed_path[_WS_NAME]

        token = self.get_host_credentials().token
        auth = DBTokenAuthentication(token)
        service_context = HybridServiceContext(subscription_id, resource_group_name,
                                               workspace_name, None, None, auth, region)
        return AzureMLRestStore(service_context=service_context,
                                host_creds=self.get_aml_host_credentials)

    def get_host_credentials(self):
        return self.adb_store.get_host_creds()

    def get_aml_host_credentials(self):
        """Construct a MlflowHostCreds to be used for obtaining fresh credentials."""
        return MlflowHostCreds(
            self.aml_store.service_context._get_run_history_url()
            + "/mlflow/v1.0" + self.aml_store.service_context._get_workspace_scope(),
            token=self.aml_store.service_context.get_auth().get_authentication_header()["Authorization"][7:])

    def create_experiment(self, *args, **kwargs):
        exp_name = kwargs['name']
        operation = "create experiment with name {}.".format(exp_name)
        try:
            exp = self.adb_store.create_experiment(*args, **kwargs)
        except Exception as e:
            handle_exception(operation, self.adb_store, e)

        kwargs['name'] = get_aml_experiment_name(exp_name)
        try:
            experiment = self.aml_store.get_experiment_by_name(kwargs['name'])
            exp_id = experiment.experiment_id if experiment else None
            if exp_id is None:
                self.aml_store.create_experiment(*args, **kwargs)
        except Exception as e:
            handle_exception(operation, self.aml_store, e)

        return exp

    def get_experiment(self, experiment_id):
        return self.reader_store.get_experiment(experiment_id)

    def get_experiment_by_name(self, experiment_name):
        return self.reader_store.get_experiment_by_name(experiment_name)

    def list_experiments(self, view_type=ViewType.ACTIVE_ONLY, max_results=None, page_token=None):
        return self.reader_store.list_experiments(view_type=view_type, max_results=max_results, page_token=page_token)

    def list_run_infos(self, experiment_id, run_view_type, *args, **kwargs):
        return self.reader_store.list_run_infos(experiment_id, run_view_type, *args, **kwargs)

    def search_runs(self, experiment_ids, filter_string, run_view_type,
                    max_results=SEARCH_MAX_RESULTS_DEFAULT, order_by=None, page_token=None):
        return self.reader_store.search_runs(experiment_ids, filter_string, run_view_type,
                                             max_results, order_by, page_token)

    def create_run(self, experiment_id, user_id, start_time, tags):
        operation = "create run"
        try:
            run = self.adb_store.create_run(experiment_id, user_id, start_time, tags)
            experiment_name = self.adb_store.get_experiment(experiment_id)._name
        except Exception as e:
            handle_exception(operation, self.adb_store, e)

        experiment_name = get_aml_experiment_name(experiment_name)
        try:
            run_dto = create_mlflow_run(self.aml_store.service_context, experiment_name,
                                        run.info.run_id, user_id, start_time, tags)
            self.aml_store.get_run(run_dto.run_id)
        except Exception as e:
            handle_exception(operation, self.aml_store, e)

        return run

    def get_run(self, run_id):
        reader_run = self.reader_store.get_run(run_id)
        reader_run._info._artifact_uri = reader_run.info.artifact_uri.replace("dbfs", "adbazureml", 1)
        return reader_run

    def get_metric_history(self, run_id, metric_key):
        return self.reader_store.get_metric_history(run_id, metric_key)

    def update_run_info(self, *args, **kwargs):
        operation = "update run info"
        execute_func(lambda store, *args, **kwargs: store.update_run_info(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)

    def log_metric(self, *args, **kwargs):
        operation = "log_metric"
        execute_func(lambda store, *args, **kwargs: store.log_metric(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)

    def log_param(self, *args, **kwargs):
        operation = "log_param"
        execute_func(lambda store, *args, **kwargs: store.log_param(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)

    def set_tag(self, *args, **kwargs):
        operation = "set_tag"
        execute_func(lambda store, *args, **kwargs: store.set_tag(*args, **kwargs),
                     self.stores, operation, *args, **kwargs)


def create_mlflow_run(service_context, experiment_name, run_id, user_id, start_time, tags):
    from azureml._restclient.run_client import RunClient

    client = RunClient(service_context, experiment_name, run_id)

    tags = {tag.key: tag.value for tag in tags}
    tags["mlflow.user"] = user_id
    sanitized_tags = {}
    for key, val in tags.items():
        if not isinstance(val, (str, type(None))):
            sanitized_tags[key] = str(val)
        else:
            sanitized_tags[key] = val

    run = client.create_run(run_id=run_id, target="sdk", run_name="run_{}".format(run_id),
                            tags=tags)
    client.post_event_start()
    return run
