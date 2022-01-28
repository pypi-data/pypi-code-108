#!/usr/bin/env python3

from hiro_graph_client.clientlib import AuthenticatedAPIHandler, AbstractTokenApiHandler


class HiroAuthz(AuthenticatedAPIHandler):
    """
    Python implementation for accessing the HIRO Authz REST API.
    See https://core.arago.co/help/specs/?url=definitions/authz.yaml
    """

    def __init__(self, api_handler: AbstractTokenApiHandler):
        """
        Constructor

        :param api_handler: External API handler.
        """
        super().__init__(api_name='authz',
                         api_handler=api_handler)

    ###############################################################################################################
    # REST API operations against the authz API
    ###############################################################################################################

    def entitlement(self, data: dict) -> dict:
        """
        Ask for entitlement decision

        HIRO REST query API: `POST self._endpoint + '/entitlement`

        :param data: Entitlement request data.
               See https://core.arago.co/help/specs/?url=definitions/authz.yaml#/[Authorization]_Entitlement/post_entitlement
        :return: The result payload
        """
        url = self.endpoint + '/entitlement'
        return self.post(url, data)
