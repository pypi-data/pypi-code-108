from msgraphy.data import ApiIterable
from msgraphy.data.file import Drive
from msgraphy.data.user import User, UserList
from msgraphy.client.graph_client import GraphResponse


class UserGraphApi:

    def __init__(self, api):
        self._api = api

    def get_user_by_principal(self, id: str) -> GraphResponse[User]:
        return self._api.client.make_request(url=f"/users/{id}", response_type=User)

    def get_user_by_email(self, email: str) -> GraphResponse[User]:
        def find_first(data):
            return UserList(data).value[0]

        return self._api.client.make_request(
            url=f"/users?$filter=startswith(mail,'{email}')",
            method="get",
            response_type=find_first
        )

    def get_user_drive(self, user: User) -> GraphResponse[Drive]:
        if user.id:
            id = user.id
        elif user.user_principal_name:
            id = user.user_principal_name
        else:
            raise ValueError("The user must have either id or user_principal_name set.")
        return self._api.client.make_request(url=f"/users/{id}/drive", method="get", response_type=Drive)

    def list_users(self, select=None):
        response_type = ApiIterable(self._api.client, User)
        params = {}
        if select:
            params['$select'] = ",".join(select)
        return self._api.client.make_request(url=f"/users", params=params, response_type=response_type)
