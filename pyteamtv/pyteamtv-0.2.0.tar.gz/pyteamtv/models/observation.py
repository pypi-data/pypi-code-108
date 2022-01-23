from .teamtv_object import TeamTVObject


class Observation(TeamTVObject):
    @property
    def observation_id(self) -> str:
        return self._observation_id

    @property
    def start_time(self) -> float:
        return self._start_time

    @property
    def trigger_time(self) -> float:
        return self._trigger_time

    @property
    def end_time(self) -> float:
        return self._end_time

    @property
    def code(self) -> str:
        return self._code

    @property
    def clock_id(self) -> str:
        return self._clock_id

    @property
    def description(self) -> str:
        return self._description

    @property
    def attributes(self) -> dict:
        return self._attributes

    def _use_attributes(self, attributes: dict):
        self._observation_id = attributes['observationId']
        self._start_time = attributes['startTime']
        self._trigger_time = attributes['triggerTime']
        self._end_time = attributes['endTime']
        self._code = attributes['code']
        self._attributes = attributes['attributes'] or dict()
        self._description = attributes['description']
        self._clock_id = attributes['clockId']
