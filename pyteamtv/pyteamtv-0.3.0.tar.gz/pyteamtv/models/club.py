from .teamtv_object import TeamTVObject


class Club(TeamTVObject):
    @property
    def name(self):
        return self._name

    @property
    def team_id(self):
        return self._club_id

    def _use_attributes(self, attributes: dict):
        self._club_id = attributes['clubId']
        self._name = attributes['name']
