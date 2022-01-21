#!/usr/bin/env python3
import json

from hiro_graph_client.clientlib import AuthenticatedAPIHandler, AbstractTokenApiHandler


class HiroKi(AuthenticatedAPIHandler):
    """
    Python implementation for accessing the HIRO Ki REST API.
    See https://core.arago.co/help/specs/?url=definitions/ki.yaml
    """

    def __init__(self, api_handler: AbstractTokenApiHandler):
        """
        Constructor

        :param api_handler: External API handler.
        """
        super().__init__(api_name='ki',
                         api_handler=api_handler)

    ###############################################################################################################
    # REST API operations against the ki API
    ###############################################################################################################

    def check(self, data: dict) -> dict:
        """
        Ask if KI is valid

        HIRO REST query API: `POST self._endpoint + '/check`

        :param data: KI validation request data.
               See https://core.arago.co/help/specs/?url=definitions/ki.yaml#/[Validatation]_Validate/post_check
        :return: The result payload
        """
        url = self.endpoint + '/check'
        return self.post(url, data)

    ###############################################################################################################
    # Internal methods
    ###############################################################################################################

    def _get_error_message(self, json_result: dict) -> str:
        """
        Intercept special error messages. These have a key 'status' in their dict.

        :param json_result: The incoming JSON containing error information.
        :return: The error message.
        """
        if 'status' in json_result:
            return json.dumps(json_result)

        return super()._get_error_message(json_result)
