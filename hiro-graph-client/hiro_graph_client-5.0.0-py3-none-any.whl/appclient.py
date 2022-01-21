#!/usr/bin/env python3

from typing import Iterator
from urllib.parse import quote_plus

from hiro_graph_client.clientlib import AuthenticatedAPIHandler, AbstractTokenApiHandler


class HiroApp(AuthenticatedAPIHandler):
    """
    Python implementation for accessing the HIRO App REST API.
    See https://core.arago.co/help/specs/?url=definitions/app.yaml
    """

    def __init__(self, api_handler: AbstractTokenApiHandler):
        """
        Constructor

        :param api_handler: External API handler.
        """
        super().__init__(api_name='app',
                         api_handler=api_handler)

    ###############################################################################################################
    # REST API operations
    ###############################################################################################################

    def get_app(self, node_id) -> dict:
        """
        HIRO REST query API: `GET self._endpoint + '/{id}'`

        :param node_id: ogit/_id of the node/vertex or edge.
        :return: The result payload
        """
        url = self.endpoint + '/' + quote_plus(node_id)
        return self.get(url)

    def get_config(self) -> dict:
        """
        HIRO REST query API: `GET self._endpoint + '/config'`. The token (internal or external) defines the config
        returned.

        :return: The result payload
        """
        url = self.endpoint + '/config'
        return self.get(url)

    def get_content(self, node_id, path) -> Iterator[bytes]:
        """
        HIRO REST query API: `GET self._endpoint + '/{id}/content/{path}'`. Get the content of an application.

        :param node_id: ogit/_id of the node/vertex or edge.
        :param path: filename / path of the desired content.
        :return: The result payload generator over binary data.
        """
        url = self.endpoint + '/' + quote_plus(node_id) + '/content/' + quote_plus(path)
        yield from self.get_binary(url)

    def get_manifest(self, node_id) -> dict:
        """
        HIRO REST query API: `GET self._endpoint + '/{id}/manifest'`. Get the manifest of an application.

        :param node_id: ogit/_id of the node/vertex or edge.
        :return: The result payload - usually with a binary content.
        """
        url = self.endpoint + '/' + quote_plus(node_id) + '/manifest'
        return self.get(url)

    def get_desktop(self) -> dict:
        """
        HIRO REST query API: `GET self._endpoint + '/desktop'`. List desktop applications.

        :return: The result payload - usually with a binary content.
        """
        url = self.endpoint + '/desktop'
        return self.get(url)
