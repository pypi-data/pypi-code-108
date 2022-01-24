# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module to define the SynapseLivyReliableHttpClient class."""

import json
import requests
from time import sleep

from azureml._base_sdk_common.common import perform_interactive_login
from azureml.core.authentication import InteractiveLoginAuthentication
from sparkmagic.livyclientlib.configurableretrypolicy import ConfigurableRetryPolicy
from sparkmagic.livyclientlib.exceptions import HttpClientException
from sparkmagic.utils.sparklogger import SparkLog
import sparkmagic.utils.configuration as conf

from . import consts


class SynapseLivyReliableHttpClient(object):
    """A http client customized to talk to Livy service."""

    def __init__(self, base_url: str):
        """Create a SynapseLivyReliableHttpClient.

        :param base_url: base url of the Livy service
        :type base_url: str
        """
        self.base_url = base_url.rstrip("/")
        self.endpoint = self.base_url
        self._auth = InteractiveLoginAuthentication()
        self._retry_policy = ConfigurableRetryPolicy(retry_seconds_to_sleep_list=conf.retry_seconds_to_sleep_list(),
                                                     max_retries=conf.configurable_retry_policy_max_retries())
        self._verify_ssl = True
        self._logger = SparkLog("SynapseLivyReliableHttpClient")
        self._session = requests.Session()

    def post_statement(self, session_id: str, data):
        """Send a POST request to run a statement.

        :param session_id: the session id
        :type session_id: str
        :param data: the code to run, as well as the kind(aka language)
        """
        return self._post("/sessions/{}/statements".format(session_id), [200, 201], data).json()

    def get_statement(self, session_id: str, statement_id: str):
        """Send a GET request to get statement status.

        :param session_id: the session id
        :type session_id: str
        :param statement_id: the statement id
        :type statement_id: str
        """
        return self._get("/sessions/{}/statements/{}".format(session_id, statement_id), [200]).json()

    def post_session(self, properties: dict):
        """Send a POST request to create a new session.

        :param properties: the session properties for the new session
        :type properties: dict
        """
        return self._post("/sessions", [200, 201], properties).json()

    def get_session(self, session_id: str, detailed: bool = False):
        """Send a GET request to get session status.

        :param session_id: the session id
        :type session_id: str
        :param detailed: whether the detail respones needed
        :type detailed: bool
        """
        return self._get("/sessions/{}{}".format(session_id, "?detailed=true" if detailed else ""), [200]).json()

    def delete_session(self, session_id: str):
        """Delete a session.

        :param session_id: the session id
        :type session_id: str
        """
        self._delete("/sessions/{}".format(session_id), [200, 404])

    def reset_session_timeout(self, session_id: str):
        """Reset the timeout of the session to keep it alive for another timeout period.

        :param session_id: the session id
        :type session_id: str
        """
        self._put("/sessions/{}/reset-timeout".format(session_id), [200])

    def get_executors(self, session_id: str, app_id: str):
        """Get all the active executors for the given application.

        :param session_id: the session id
        :type session_id: str
        :param app_id: application id
        :type app_id: str
        """
        return self._get("/sessions/{0}/applications/{1}/executors".format(session_id, app_id), [200]).json()

    def get_jobs(self, session_id: str, app_id: str):
        """Get all jobs for the given application.

        :param session_id: the session id
        :type session_id: str
        :param app_id: application id
        :type app_id: str
        """
        return self._get("/sessions/{0}/applications/{1}/jobs".format(session_id, app_id), [200]).json()

    def get_job_by_id(self, session_id: str, app_id: str, job_id: str):
        """Get status of a given job.

        :param session_id: the session id
        :type session_id: str
        :param app_id: application id
        :type app_id: str
        :param job_id: job id
        :type job_id: str
        """
        return self._get("/sessions/{0}/applications/{1}/jobs/{2}".format(session_id, app_id, job_id), [200]).json()

    def get_stages(self, session_id: str, app_id: str):
        """Get all stages of a given application.

        :param session_id: the session id
        :type session_id: str
        :param app_id: application id
        :type app_id: str
        """
        return self._get("/sessions/{0}/applications/{1}/stages".format(session_id, app_id), [200]).json()

    def get_stage_by_id(self, session_id: str, app_id: str, stage_id: str):
        """Get all attempts of a given stage.

        :param session_id: the session id
        :type session_id: str
        :param app_id: application id
        :type app_id: str
        :param stage_id: stage id
        :type stage_id: str
        """
        return self._get("/sessions/{0}/applications/{1}/stages/{2}".format(session_id, app_id, stage_id), [200]) \
                   .json()

    def get_stage_attempt_by_id(self, session_id: str, app_id: str, stage_id: str, attempt_id: str):
        """Get status of a given attempt.

        :param session_id: the session id
        :type session_id: str
        :param app_id: application id
        :type app_id: str
        :param stage_id: stage id
        :type stage_id: str
        :param attempt_id: attempt id
        :type attempt_id: str
        """
        return self._get(
            "/sessions/{0}/applications/{1}/stages/{2}/{3}".format(session_id, app_id, stage_id, attempt_id),
            [200]).json()

    def get_all_session_logs(self, session_id: str):
        """Get all logs of a given session.

        :param session_id: the session id
        :type session_id: str
        """
        try:
            # Synapse does not implement this livy api
            return self._get("/sessions/{}/log?from=0".format(session_id), [200]).json()
        except Exception:
            return {"log": []}

    def _get_headers(self):
        try:
            token = self._auth._get_resource_token(resource=consts.CREDENTIALS_resource)
        except Exception:
            print("Performing interactive authentication. Please follow the instructions "
                  "on the terminal.")
            perform_interactive_login(tenant=self._auth._tenant_id, cloud_type=self._auth._cloud_type)
            print("Interactive authentication successfully completed.")
            token = self._auth._get_resource_token(resource=consts.CREDENTIALS_resource)
        return {
            'Authorization': "Bearer {}".format(token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def _get(self, relative_url, accepted_status_codes):
        return self._send_request(relative_url, accepted_status_codes, self._session.get)

    def _post(self, relative_url, accepted_status_codes, data=None):
        return self._send_request(relative_url, accepted_status_codes, self._session.post, data)

    def _put(self, relative_url, accepted_status_codes, data=None):
        return self._send_request(relative_url, accepted_status_codes, self._session.put, data)

    def _delete(self, relative_url, accepted_status_codes):
        return self._send_request(relative_url, accepted_status_codes, self._session.delete)

    def _send_request(self, relative_url, accepted_status_codes, function, data=None):
        return self._send_request_helper(self.base_url + relative_url, accepted_status_codes, function, data, 1)

    def _send_request_helper(self, url, accepted_status_codes, function, data, retry_count):
        while True:
            try:
                headers = self._get_headers()
                if data is None:
                    r = function(url, headers=headers, verify=self._verify_ssl, timeout=60)
                else:
                    r = function(url, headers=headers, data=json.dumps(data), verify=self._verify_ssl, timeout=60)
            except requests.exceptions.RequestException as e:
                error = True
                r = None
                status = None
                text = None
                self._logger.error("Request to '{}' failed with '{}'".format(url, e))
            else:
                error = False
                status = r.status_code
                text = r.text

            if error or status not in accepted_status_codes:
                if self._retry_policy.should_retry(status, error, retry_count):
                    sleep(self._retry_policy.seconds_to_sleep(retry_count))
                    self._logger.info("Status '{}'. Retry the request for '{}' times".format(status, retry_count))
                    retry_count += 1
                    continue

                if error:
                    raise HttpClientException("Error sending http request and please retry later.")
                else:
                    raise HttpClientException(
                        "Invalid status code '{}' from {} with error: {}.".format(status, url, text))

            return r
