# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Synapse Session module."""

import json
import textwrap
import uuid
import time

from azureml.core.authentication import InteractiveLoginAuthentication
from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
from sparkmagic.livyclientlib.exceptions import LivyClientTimeoutException, LivyUnexpectedStatusException, \
    HttpClientException
from sparkmagic.livyclientlib.livysession import LivySession
from sparkmagic.utils.constants import POSSIBLE_SESSION_STATUS, IDLE_SESSION_STATUS, FINAL_STATUS
from hdijupyterutils.ipythondisplay import IpythonDisplay
from azure.mgmt.synapse import SynapseManagementClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

from . import consts
from . import utils
from .synapseerrorparser import SynapseErrorParser
from .sessiontracker import SessionTracker
from .synapselivyreliablehttpclient import SynapseLivyReliableHttpClient
from . import telemetryutils


class SynapseSession(LivySession):
    """SynapseSession class wraps LivySession and add some Synapse specific session handling."""

    def __init__(self, subscription_id: str, resource_group: str, workspace: str, sparkpool: str,
                 properties: dict, timeout: int, ipython_display: IpythonDisplay, amlwslocation: str):
        """Create the SynapseSession.

        :param subscription_id: subscription id
        :type subscription_id: str
        :param workspace: name of the Synapse workspace
        :type workspace: str
        :param sparkpool: name of the Synapse Spark pool
        :type sparkpool: str
        :param timeout: how long the session will timeout, in minutes
        :type timeout: int
        :param properties: a dictionary contains the settings of the session
        :type properties: dict
        :param ipython_display: ipython display
        :type ipython_display: IpythonDisplay
        :param amlwslocation: aml ws location
        :type amlwslocation: str
        """
        # using amlwslocation for getting endpoint as it depend on cloud type
        # cloud type should always be same for synapse ws and aml workspace
        endpoint_url = utils.get_synapse_endpoint(workspace, sparkpool, amlwslocation)
        self._http_client = SynapseLivyReliableHttpClient(endpoint_url)
        super(SynapseSession, self).__init__(self._http_client, properties, ipython_display)
        self.meta = {}
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace = workspace
        self.sparkpool = sparkpool
        self.amlwslocation = amlwslocation
        self.session_tracker = None
        self.error = None
        self.timeout = timeout
        self.is_timeout = False
        self.show_dot_progress = False
        self._auth = InteractiveLoginAuthentication()
        telemetryutils.set_synapse_session_guid(str(self.guid))

    def start(self, timeout=None):
        """Start the session."""
        # Override the LivySession.start to init SessionTracker and meta, and set the start timeout
        # to None (no timeout) by default
        self._printed_resource_warning = False  # reset
        try:
            name = self.properties["name"]
            env_desc = utils._get_env_desc(self.properties.get('environment'),
                                           self.properties.get('environmentVersion'))
            if env_desc is not None:
                self._enable_session_level_package()
                utils.write("Starting session '{}' under environment '{}', this may take several minutes "
                            .format(name, env_desc))
            else:
                utils.write("Starting session '{}', this may take several minutes ".format(name))
            r = self._http_client.post_session(self.properties)
            self.id = r[u"id"]
            self.status = str(r[u"state"])

            # Wait for timeout seconds since the warm up of Synapse takes longer then normal Spark.
            self.show_dot_progress = True
            self.wait_for_idle(timeout)
            utils.writeln(" Succeeded!")
        except LivyClientTimeoutException:
            raise LivyClientTimeoutException(
                "Session {} did not start up in {} seconds. Consider removing --start-timeout or try later."
                .format(self.id, timeout))
        except LivyUnexpectedStatusException:
            # get detail session status for detail error msg
            livy_err_info = ""
            try:
                response = self._http_client.get_session(self.id, True)
                livy_err_info = self._set_error_details(str(response['errorInfo']))
            finally:
                raise LivyUnexpectedStatusException(
                    "Start session failed at status {}. \n"
                    "Error info: {} \n"
                    "Please retry or go to Synapse portal {} for details."
                    .format(self.status, livy_err_info, self.get_synapse_app_url()))
        except HttpClientException as e:
            livy_err_info = self._set_error_details(str(e))
            raise HttpClientException(
                "Start session failed at status {}. \n"
                "Error info: {} \n"
                "Please retry or go to Synapse portal {} for details."
                .format(self.status, livy_err_info, self.get_synapse_app_url()))
        aml_workspace_details = telemetryutils.get_aml_workspace_details()
        self.meta = {
            "subscription_id": aml_workspace_details.get("subscription_id", None),
            "resource_group": aml_workspace_details.get("resource_group", None),
            "workspace_name": aml_workspace_details.get("workspace_name", None),
            "session_id": self.id,
            "application_id": self._app_id,
            "application_name": name,
            "application_url": self.get_synapse_app_url(),
            "spark_ui_url": self.get_spark_ui_url(),
            "driver_memory": self.properties["driverMemory"],
            "driver_cores": self.properties["driverCores"],
            "executor_memory": self.properties["executorMemory"],
            "executor_cores": self.properties["executorCores"],
            "num_executors": self.properties["numExecutors"],
            "environment_name": self.properties.get("environment"),
            "environment_version": self.properties.get("environmentVersion"),
            "spark_conf": self.properties.get("conf"),
            "start_timeout_seconds": self.properties["startTimeout"],
            "timeout_minutes": self.timeout,
            "synapse_session_guid": str(self.guid),
        }
        self.session_tracker = SessionTracker(self)
        self.session_tracker.session_create_end()

    def _set_error_details(self, error_info: str):
        livy_err_info = error_info
        synapse_error_details = SynapseErrorParser.get_error_details(error_info)
        if synapse_error_details.error_message is not None:
            livy_err_info = "{}: {}".format(synapse_error_details.error_code,
                                            synapse_error_details.error_message)
        return livy_err_info

    def get_synapse_app_url(self):
        """Get the url of the Synapse Spark application."""
        if self.subscription_id is None or self.resource_group is None or self.amlwslocation is None:
            return "unknown"
        if self.amlwslocation in consts.US_GOV_CLOUD:
            return consts.SYNAPSE_UI_URL_TEMPLATE.format(consts.SYNAPSE_UI_DNS_USGOV,
                                                         self._app_id,
                                                         self.subscription_id,
                                                         self.resource_group,
                                                         self.workspace,
                                                         self.id,
                                                         self.sparkpool)
        elif self.amlwslocation in consts.MOONCAKE_CLOUD:
            return consts.SYNAPSE_UI_URL_TEMPLATE.format(consts.SYNAPSE_UI_DNS_MOONCAKE,
                                                         self._app_id,
                                                         self.subscription_id,
                                                         self.resource_group,
                                                         self.workspace,
                                                         self.id,
                                                         self.sparkpool)
        elif self.amlwslocation in consts.BLACKFOREST_CLOUD:
            return consts.SYNAPSE_UI_URL_TEMPLATE.format(consts.SYNAPSE_UI_DNS_BLACKFOREST,
                                                         self._app_id,
                                                         self.subscription_id,
                                                         self.resource_group,
                                                         self.workspace,
                                                         self.id,
                                                         self.sparkpool)
        else:
            return consts.SYNAPSE_UI_URL_TEMPLATE.format(consts.SYNAPSE_UI_DNS,
                                                         self._app_id,
                                                         self.subscription_id,
                                                         self.resource_group,
                                                         self.workspace,
                                                         self.id,
                                                         self.sparkpool)

    def get_spark_ui_url(self):
        """Get the url of the Spark UI."""
        if self.amlwslocation in consts.US_GOV_CLOUD:
            return consts.SPARK_UI_URL_TEMPLATE_UPDATED.format(consts.SPARK_UI_DNS_USGOV,
                                                               self._get_tenant_id(),
                                                               consts.LIVY_ENDPOINT_DNS_USGOV,
                                                               self.workspace,
                                                               self.sparkpool,
                                                               self.id,
                                                               self._app_id)
        elif self.amlwslocation in consts.MOONCAKE_CLOUD:
            return consts.SPARK_UI_URL_TEMPLATE_UPDATED.format(consts.SPARK_UI_DNS_MOONCAKE,
                                                               self._get_tenant_id(),
                                                               consts.LIVY_ENDPOINT_DNS_MOONCAKE,
                                                               self.workspace,
                                                               self.sparkpool,
                                                               self.id,
                                                               self._app_id)
        elif self.amlwslocation in consts.BLACKFOREST_CLOUD:
            return consts.SPARK_UI_URL_TEMPLATE_UPDATED.format(consts.SPARK_UI_DNS_BLACKFOREST,
                                                               self._get_tenant_id(),
                                                               consts.LIVY_ENDPOINT_DNS_BLACKFOREST,
                                                               self.workspace,
                                                               self.sparkpool,
                                                               self.id,
                                                               self._app_id)
        else:
            return consts.SPARK_UI_URL_TEMPLATE_UPDATED.format(consts.SPARK_UI_DNS,
                                                               self._get_tenant_id(),
                                                               consts.LIVY_ENDPOINT_DNS,
                                                               self.workspace,
                                                               self.sparkpool,
                                                               self.id,
                                                               self._app_id)

    def show_meta(self):
        """Show session meta data in notebook."""
        self.meta["application_state"] = self.status
        utils.writeln(json.dumps(self.meta, indent=4, sort_keys=True))

    def delete(self):
        """Delete the session."""
        self.session_tracker.session_delete_end()
        telemetryutils.remove_synapse_session_guid()
        try:
            super(SynapseSession, self).delete()
        except Exception:
            raise

    def execute(self, code: str, kind):
        """Execute some Spark code.

        :param code: the Spark code to be executed
        :type code: str
        :param kind: the Spark language of the code, supported language include: spark(Scala), pyspark, csharp and sql
        :type kind: str
        """
        assert self.can_submit()
        assert code is not None
        assert kind is not None
        self.show_dot_progress = False
        try:
            self.wait_for_idle()
        except LivyUnexpectedStatusException:
            raise LivyUnexpectedStatusException(
                "Session failed at status {}. "
                "Please run stop and start a new session or go to Synapse portal {} for details.".format(
                    self.status,
                    self.get_synapse_app_url()))
        code = textwrap.dedent(code)
        response = self.http_client.post_statement(self.id, {"code": code, "kind": kind})
        statement_id = response[u'id']
        # here is the trick, we are not able to get the real cell id from frontend, just create a new guid for it
        # but since there will be only one running cell in notebook, frontend can match this new guid to it
        self.session_tracker.statement_execution_start(str(uuid.uuid4()), statement_id)

    def wait_for_idle(self, seconds_to_wait=None):
        """Wait for session to go to idle status. Sleep meanwhile.
        This overrides the parent method. Timeout can be None, which will depend on Synapse to
        manage session life cycle.
        """
        printed_long_session_start = False
        retries = 1
        start_time = time.time()

        while True:
            self.refresh_status_and_info()
            if self.status == IDLE_SESSION_STATUS:
                return

            if self.status in FINAL_STATUS:
                error = u"Session {} unexpectedly reached final status '{}'."\
                    .format(self.id, self.status)
                self.logger.error(error)
                raise LivyUnexpectedStatusException(u'{} See logs:\n{}'.format(error, self.get_logs()))

            if self.show_dot_progress and not printed_long_session_start:
                if time.time() - start_time > 300:
                    self.ipython_display.send_error("Starting session is taking longer than expected. Please "
                                                    + "wait for session start to complete.")
                printed_long_session_start = True

            prev_time = time.time()
            sleep_time = self._policy.seconds_to_sleep(retries)
            retries += 1

            self.logger.debug(u"Session {} in state {}. Sleeping {} seconds."
                              .format(self.id, self.status, sleep_time))
            self.sleep(sleep_time)

            if seconds_to_wait:
                if seconds_to_wait <= 0.0:
                    error = u"Session {} did not reach idle status in time. Current status is {}."\
                        .format(self.id, self.status)
                    self.logger.error(error)
                    raise LivyClientTimeoutException(error)

                seconds_to_wait -= time.time() - prev_time

    def refresh_status_and_info(self):
        """Refresh the latest status of the session."""
        # Override the one from LivySession to get appId and print dots for long session start
        if self.show_dot_progress:
            utils.write(".")
        response = self._refresh_status()
        log_array = response[u'log']
        if log_array:
            self.session_info = "\n".join(log_array)

    def _refresh_status(self):
        response = self._http_client.get_session(self.id)
        status = response[u"state"]
        if status in POSSIBLE_SESSION_STATUS:
            self.status = status
            if self._app_id is None and response[u"appId"]:
                self._app_id = response[u"appId"]
        else:
            raise LivyUnexpectedStatusException("Status '{}' not supported by session.".format(status))
        self._reset_timeout_when_needed()
        return response

    def mark_timeout(self):
        """Mark the session as a timeout session to let it timeout."""
        self.status = consts.SESSION_STATUS_TIMEOUT
        self.is_timeout = True

    def can_submit(self):
        """Check if we can submit a job within this session."""
        is_final_status = self.status in FINAL_STATUS
        return not is_final_status and not self.is_timeout

    def _reset_timeout_when_needed(self):
        if IDLE_SESSION_STATUS == self.status and not self.is_timeout:
            self._http_client.reset_session_timeout(self.id)

    def _get_tenant_id(self):
        token = self._auth._get_resource_token(resource=consts.CREDENTIALS_resource)
        tenant_id = fetch_tenantid_from_aad_token(token)

        return tenant_id

    def _enable_session_level_package(self):
        credential = DefaultAzureCredential()
        syn_mgmt_client = SynapseManagementClient(credential, self.subscription_id)
        try:
            pool_info = syn_mgmt_client.big_data_pools.get(self.resource_group, self.workspace, self.sparkpool)
            if pool_info.session_level_packages_enabled:
                return
        except Exception:
            # not able to get the session_level_packages flag, most likely authorization issue
            # show a warning msg and return
            utils.writeln('Warning: pool may not support session level packages, you may want to double check'
                          'that with admin.')
            return

        err_msg = 'Fail to enable session level packages for the Synapse Spark pool! Ask admin to enable it.'
        try:
            pool_info.session_level_packages_enabled = True
            poller = syn_mgmt_client.big_data_pools.begin_create_or_update(self.resource_group, self.workspace,
                                                                           self.sparkpool, pool_info)
            utils.write('Enabling session level packages for the Synapse Spark pool ')
            while not poller.done():
                utils.write('.')
                time.sleep(1)
            if poller.result().session_level_packages_enabled:
                utils.writeln(' Enabled')
            else:
                raise Exception(err_msg)
        except HttpResponseError as hre:
            if 'AuthorizationFailed' in str(hre):
                raise Exception('Not authorized to enable session level packages for the Synapse Spark pool!'
                                ' Ask admin to enable it.') from hre
            else:
                raise Exception(err_msg) from hre
        except Exception as e:
            raise Exception(err_msg) from e
