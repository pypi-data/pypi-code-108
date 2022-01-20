import typing
from typing import Union

from msgraphy.client.graph_client import GraphResponse
from msgraphy.data import ApiIterable, ListResponse
from msgraphy.data.list import List, ListColumn
from msgraphy.data.sharepoint import SiteResource


class ListGraphApi:

    def __init__(self, api):
        self._api = api

    def get_list(self, site: SiteResource, list_name: str) -> GraphResponse[List]:
        return self._api.client.make_request(url=f"{site.resource}/lists/{list_name}", response_type=List)

    def get_columns(self, site: SiteResource, list_name: str) -> GraphResponse[ListResponse[ListColumn]]:
        response_type = ApiIterable(self._api.client, ListColumn)
        return self._api.client.make_request(url=f"{site.resource}/lists/{list_name}/columns",
                                             response_type=response_type)

    def get_items(self, site: SiteResource, list_name: str,
                  fields: Union[str, bool] = None,
                  filter: str = None,
                  ) -> GraphResponse[ListResponse[List]]:

        params = {}
        if isinstance(fields, bool) and fields:
            params['expand'] = "fields"
        elif isinstance(fields, str):
            params['expand'] = f"fields(select={fields})"

        if filter is not None:
            params['filter'] = filter

        response_type = ApiIterable(self._api.client, List)

        response = self._api.client.make_request(
            url=f"{site.resource}/lists/{list_name}/items",
            params=params,
            response_type=response_type,
        )
        return response

    def get_users_list(self, site: SiteResource, fields: Union[str, bool] = None) -> GraphResponse[ListResponse[List]]:
        if fields is None:
            fields = "Title,EMail,JobTitle,FirstName,LastName,WorkPhone,UserName,UserSelection"
        return self.get_items(site, "User Information List", fields=fields)

    def update_item(self, site: SiteResource, list_name: str, item_id: int, data: typing.Mapping):
        return self._api.client.make_request(
            method='patch',
            url=f"{site.resource}/lists/{list_name}/items/{item_id}/fields",
            json=data
        )

    def add_item(self, site: SiteResource, list_name: str, data: typing.Mapping):
        return self._api.client.make_request(
            method='post',
            url=f"{site.resource}/lists/{list_name}/items",
            json=dict(fields=data)
        )

    def delete_list(self, site, list_name):
        return self._api.client.make_request(
            method='delete',
            url=f"{site.resource}/lists/{list_name}",
        )

    def create_list(self, site, list_name, columns, display_name=None):
        data = {
            "displayName": display_name if display_name else list_name,
            "columns": columns
        }
        return self._api.client.make_request(
            method='post',
            url=f"{site.resource}/lists",
            json=data
        )
