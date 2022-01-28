from typing import Type, Set, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from pyteamtv.models.sporting_event import SportingEvent

from pyteamtv.infra.requester import Requester
from pyteamtv.models.list import List
from pyteamtv.models.observation import Observation


def pol2cart(angle: float, distance: float):
    if angle > 90:
        angle -= 360
    angle += 90

    phi = (angle / 360) * 2 * math.pi
    rho = distance

    x = rho * math.cos(phi)
    y = rho * math.sin(phi)
    return x, y


class ObservationLog(List[Observation]):
    def __init__(self,
                 content_class: Type[Observation],
                 requester: Requester,
                 method: str,
                 url: str,
                 clock_id: str,
                 sporting_event: 'SportingEvent'
                 ):
        super().__init__(content_class, requester, method, url)
        self._clock_id = clock_id
        self._sporting_event = sporting_event

    def get_mapping_stats(self):
        stats = dict(
            success=0,
            failed=0
        )
        for observation in self:
            if observation.clock_id == self._clock_id:
                stats['success'] += 1
            else:
                stats['failed'] += 1
        return stats

    def to_pandas(self):
        try:
            import pandas as pd
        except ImportError:
            raise Exception("You don't have pandas installed. Please install first")

        observations = []
        skip_attributes = {"teamId", "personId", "team", "person", "inPerson", "inPersonId", "outPerson", "outPersonId"}
        team = dict()
        for observation in self:
            if observation.code == 'START-POSSESSION':
                team = dict(
                    team_id=observation.attributes['teamId'],
                    team_name=observation.attributes['team']['name'],
                    team_ground=observation.attributes['team']['ground'],
                    position=observation.attributes['position']
                )
            else:
                if 'person' in observation.attributes:
                    person = dict(
                        person_id=observation.attributes['personId'],
                        first_name=observation.attributes['person']['firstName'],
                        last_name=observation.attributes['person']['lastName'],
                        number=observation.attributes['person']['number']
                    )
                    person['full_name'] = person['first_name'] + ' ' + person['last_name']
                else:
                    person = dict()

                attributes = dict()
                attributes.update(team)
                attributes.update(person)
                for k, v in observation.attributes.items():
                    if k not in skip_attributes:
                        attributes[k] = v

                if 'angle' in attributes and 'distance' in attributes:
                    attributes['x'], attributes['y'] = pol2cart(
                        attributes['angle'], attributes['distance']
                    )

                observation_dict = dict(
                    sporting_event_id=self._sporting_event.sporting_event_id,
                    sporting_event_name=self._sporting_event.name,
                    sporting_event_scheduled_at=self._sporting_event.scheduled_at,
                    observation_id=observation.observation_id,
                    clock_id=observation.clock_id,
                    start_time=observation.start_time,
                    end_time=observation.end_time,
                    code=observation.code,
                    description=observation.description,
                    **attributes
                )

                observations.append(observation_dict)

        return pd.DataFrame.from_records(observations)
