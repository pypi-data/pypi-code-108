import jwt

from pyteamtv.infra.requester import Requester
from pyteamtv.models.resource_group.factory import factory as resource_group_factory
from .endpoint import API_ENDPOINT

from .token import TOKEN


class TeamTVApp(object):
    def __init__(self, jwt_token, app_id: str):
        self.jwt_token = jwt_token

        token = jwt.decode(
           jwt_token,
           TOKEN,
           algorithms='RS256',
           verify=True,
           audience=f"app:{app_id}"
        )

        self._requester = Requester(
            f"{API_ENDPOINT}/api",
            jwt_token
        )
        self.__token = token

    def get_resource_group(self):
        """
        :rtype: :class:`pyteamtv.resource_group.team.Team`
        """
        data = self._requester.request(
           "GET",
           "/resourceGroups/current"
        )

        return resource_group_factory(
           self._requester,
           data
        )
