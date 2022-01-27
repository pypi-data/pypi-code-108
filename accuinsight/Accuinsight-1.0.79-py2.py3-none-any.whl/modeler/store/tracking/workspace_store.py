import logging

from Accuinsight.modeler.utils.rest_utils import http_request, verify_rest_response
from Accuinsight.modeler.utils.os_getenv import get_os_env
from Accuinsight.modeler.core.LcConst import LcConst


class RestStore:
    def __init__(self, host_creds):
        if host_creds is None:
            raise Exception("host_creds cannot be None")

        self._host_creds = host_creds

    @property
    def host_creds(self):
        return self._host_creds

    @staticmethod
    def set_endpoint_uri(endpoint, mode):
        if mode == "alarm":
            return endpoint + '/alarm'
        elif mode == "run":
            return endpoint + '/afterRun'
        else:
            return endpoint

    def call_endpoint(self, json_body, mode):
        env_value = get_os_env()

        endpoint = self.set_endpoint_uri('/project/{project}/workspace/{workspaceId}', mode)
        endpoint = endpoint.replace('{project}', str(env_value[LcConst.ENV_PROJECT_ID]))
        endpoint = endpoint.replace('{workspaceId}', str(env_value[LcConst.ENV_WORKSPACE_ID]))

        try:
            response = http_request(host_creds=self.host_creds, endpoint=endpoint, method='POST', data=json_body)
            response = verify_rest_response(response, endpoint).text

        except Exception as e:
            logging.error("Modeler API server connection failed", e)
            response = None

        return response
