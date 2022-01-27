import logging

from Accuinsight.modeler.utils.rest_utils import http_request, verify_rest_response
from Accuinsight.modeler.utils.os_getenv import get_os_env
from Accuinsight.modeler.core.MonitoringConst.deploy import DeployConst


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
            return endpoint + '/monitoring/alarm'
        elif mode == "log_summary":
            return endpoint + '/monitoring/summary'
        elif mode == "log_data":
            return endpoint + '/monitoring/data'
        else:
            return endpoint + '/monitoring'

    def call_endpoint(self, method, json_body, mode):
        env_value = get_os_env('MONITORING_DEPLOY')
        endpoint = self.set_endpoint_uri('/project/{projectId}/deploy/{deployId}', mode)
        endpoint = endpoint.replace('{projectId}', str(env_value[DeployConst.ENV_PROJECT_ID]))
        endpoint = endpoint.replace('{deployId}', str(env_value[DeployConst.ENV_DEPLOY_ID]))

        try:
            if method == 'GET':
                response = http_request(
                    host_creds=self.host_creds, endpoint=endpoint, method=method)
            else:
                response = http_request(
                    host_creds=self.host_creds, endpoint=endpoint, method=method, data=json_body)

            response = verify_rest_response(response, endpoint).text

        except Exception as e:
            logging.error("Modeler API server connection failed: ", e)
            response = None

        return response
