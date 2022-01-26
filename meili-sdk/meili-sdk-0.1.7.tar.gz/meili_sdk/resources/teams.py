from meili_sdk.models.team import Team
from meili_sdk.resources.base import BaseResource


class TeamResource(BaseResource):
    def get_teams(self):
        return self.get("api/teams/", expected_class=Team)

    def update_team(self, team):
        return self.patch(f"api/teams/{team.uuid}/", data=team, expected_class=Team)

    def delete_team(self, team):
        return self.delete(f"api/teams/{team.uuid}/")


class SDKTeamResource(BaseResource):
    def get_teams(self):
        return self.get("sdk/teams/", expected_class=Team)

    def update_team(self, team):
        return self.patch(f"sdk/teams/{team.uuid}/", data=team, expected_class=Team)
