from .teamtv_object import TeamTVObject


class Team(TeamTVObject):
    @property
    def name(self):
        return self._name

    @property
    def team_id(self):
        return self._team_id

    @property
    def sport_type(self):
        return self._sport_type

    @property
    def tags(self):
        return self._tags

    def _use_attributes(self, attributes: dict):
        self._team_id = attributes['teamId']
        self._name = attributes['name']
        self._sport_type = attributes['sportType']
        self._tags = attributes.get('tags', {})
