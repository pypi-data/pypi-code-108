from msgraphy.client.graph_client import GraphResponse, URL_BETA
from msgraphy.data import ListResponse, ApiIterable
from msgraphy.data.file import DriveItem
from msgraphy.data.group import Group
from msgraphy.data.team import Team, Channel


class TeamGraphApi:

    def __init__(self, api):
        self._api = api

    def get_team(self, team_id) -> GraphResponse[Team]:
        return self._api.client.make_request(url=f"/teams/{team_id}", response_type=Team)

    def list_teams(self, search=None, starts_with=None, exact=None) -> GraphResponse[ListResponse[Group]]:
        filter_query = "resourceProvisioningOptions/any(x:x eq 'Team')"
        if exact:
            filter_query = f"{filter_query} and displayName eq '{exact}'"
        elif starts_with:
            filter_query = f"{filter_query} and startsWith(displayName,'{starts_with}')"

        params = {"$filter": filter_query}
        headers = {}

        if search:
            params["$search"] = f'"displayName:{search}"'
            headers["ConsistencyLevel"] = "eventual"

        return self._api.client.make_request(
            url=f"{URL_BETA}groups",
            headers=headers,
            params=params,
            response_type=ApiIterable(self._api.client, Group),
        )

    def create_team(self, team: Team, template: str = "https://graph.microsoft.com/v1.0/teamsTemplates('standard')"):
        data = team.asdict()
        data['template@odata.bind'] = template
        return self._api.client.make_request(url="/teams", method="post", json=data)

    def list_channels(self, team_id) -> GraphResponse[ListResponse[Channel]]:
        response_type = ApiIterable(self._api.client, Channel)
        return self._api.client.make_request(url=f"/teams/{team_id}/channels", response_type=response_type)

    def get_primary_channel(self, team_id) -> GraphResponse[Channel]:
        return self._api.client.make_request(url=f"/teams/{team_id}/primaryChannel", response_type=Channel)

    def add_tab_to_channel(self, team_id, channel_id, tab_name, tab_url):
        tab_data = {
            "displayName": tab_name,
            "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.web",
            "configuration": {
                "contentUrl": tab_url,
                "websiteUrl": tab_url,
            },
        }
        url = f"/teams/{team_id}/channels/{channel_id}/tabs"
        return self._api.client.make_request(url=url, method="post", json=tab_data)

    def get_channel_files_folder(self, team_id, channel_id) -> GraphResponse[DriveItem]:
        return self._api.client.make_request(url=f"/teams/{team_id}/channels/{channel_id}/filesFolder",
                                             response_type=DriveItem)

