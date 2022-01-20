from msgraphy.client.graph_client import GraphResponse
from msgraphy.data import ApiIterable, ListResponse
from msgraphy.data.group import Group
from msgraphy.data.user import User


class GroupGraphApi:

    def __init__(self, api):
        self._api = api

    def get_group_by_id(self, group_id: str) -> GraphResponse[Group]:
        return self._api.client.make_request(url=f"/groups/{group_id}", response_type=Group)

    def delete(self, group_id: str) -> GraphResponse[Group]:
        return self._api.client.make_request(url=f"/groups/{group_id}", method="delete")

    def list_groups(self) -> GraphResponse[ListResponse[Group]]:
        response_type = ApiIterable(self._api.client, Group)
        return self._api.client.make_request(url=f"/groups", response_type=response_type)

    def list_group_members(self, id):
        response_type = ApiIterable(self._api.client, User)
        return self._api.client.make_request(url=f"/groups/{id}/members", response_type=response_type)

    def list_group_owners(self, id):
        response_type = ApiIterable(self._api.client, User)
        return self._api.client.make_request(url=f"/groups/{id}/owners", response_type=response_type)
