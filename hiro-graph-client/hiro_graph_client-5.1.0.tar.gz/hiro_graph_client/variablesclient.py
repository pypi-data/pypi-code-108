#!/usr/bin/env python3
from typing import List, Dict, Union

from hiro_graph_client.clientlib import AuthenticatedAPIHandler, AbstractTokenApiHandler


class HiroVariables(AuthenticatedAPIHandler):
    """
    Python implementation for accessing the HIRO Variables REST API.
    See https://core.arago.co/help/specs/?url=definitions/variables.yaml
    """

    def __init__(self, api_handler: AbstractTokenApiHandler):
        """
        Constructor

        :param api_handler: External API handler.
        """
        super().__init__(api_name='variables',
                         api_handler=api_handler)

    ###############################################################################################################
    # REST API operations against the variable API
    ###############################################################################################################

    def create_variable(self,
                        data: dict,
                        subtype: str = None) -> dict:
        """
        Creates new variable

        HIRO REST query API: `PUT self._endpoint`

        :param data: Variable content.
               See https://core.arago.co/help/specs/?url=definitions/variables.yaml#/[Variables]/put_
        :param subtype Query variable. Value of ogit/subType. Optional.
        :return: The result payload
        """
        query = {
            "subtype": subtype
        }

        url = self.endpoint + self._get_query_part(query)
        return self.put(url, data)

    def get_variable(self,
                     name: str) -> dict:
        """
        Get variable by name. (synonym for self.define(name))

        HIRO REST query API: `GET self._endpoint + '/define'`

        :param name Variable name. Required.
        :return: The result payload
        """
        return self.define(name)

    def define(self,
               name: str) -> dict:
        """
        Get variable by name.

        HIRO REST query API: `GET self._endpoint + '/define'`

        :param name Variable name. Required.
        :return: The result payload
        """
        query = {
            "name": name
        }

        url = self.endpoint + "/define" + self._get_query_part(query)
        return self.get(url)

    def like(self,
             name: str,
             description: str = None,
             subtype: str = None,
             full: bool = None) -> Union[List, Dict]:
        """
        Search for similar variables.

        HIRO REST query API: `GET self._endpoint + '/like'`

        :param name Variable name. Required.
        :param description: Search by variable description. Optional.
        :param subtype: Value of ogit/subType. Optional.
        :param full: Return full variable, not just a name. Optional. Default false.
        :return: The result payload. Either a list of dict or a dict with an error message.
        """
        query = {
            "name": name,
            "description": description,
            "subtype": subtype,
            "full": full
        }

        url = self.endpoint + "/like" + self._get_query_part(query)
        res = self.get(url)
        if 'error' in res:
            return res
        res_list: list = res['items']
        return res_list

    def suggest(self,
                name: str,
                subtype: str = None,
                full: bool = None) -> Union[List, Dict]:
        """
        Search for similar variables.

        HIRO REST query API: `GET self._endpoint + '/suggest'`

        :param name Variable name. Required.
        :param subtype: Value of ogit/subType. Optional.
        :param full: Return full variable, not just a name. Optional. Default false.
        :return: The result payload. Either a list of dict or a dict with an error message.
        """
        query = {
            "name": name,
            "subtype": subtype,
            "full": full
        }

        url = self.endpoint + "/suggest" + self._get_query_part(query)
        res = self.get(url)
        if 'error' in res:
            return res
        res_list: list = res['items']
        return res_list
