from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session
from threedi_api_client.openapi.models.lateral import Lateral
from threedi_modelchecker.simulation_templates.exceptions import (
    SchematisationError,
)
from threedi_modelchecker.simulation_templates.utils import parse_timeseries
from threedi_modelchecker.simulation_templates.utils import (
    strip_dict_none_values,
)
from threedi_modelchecker.threedi_model.models import Lateral1d
from threedi_modelchecker.threedi_model.models import Lateral2D
from typing import List

import json


def lateral_1d_to_api_lateral(lateral_1d: Lateral1d) -> Lateral:
    try:
        values = parse_timeseries(lateral_1d.timeseries)
    except (ValueError, TypeError):
        raise SchematisationError(
            f"Incorrect timeseries format for lateral 1D with id: {lateral_1d.id}"
        )

    offset = values[0][0]

    if offset > 0:
        # Shift timeseries to start at t=0
        values = [[x[0] - offset, x[1]] for x in values]

    return Lateral(
        connection_node=int(lateral_1d.connection_node_id),
        offset=int(values[0][0]),
        values=values,
        units="m3/s",
        interpolate=False,
    )


def lateral_2d_to_api_lateral(lateral_2d: Lateral2D, session: Session) -> Lateral:
    try:
        values = parse_timeseries(lateral_2d.timeseries)
    except (ValueError, TypeError):
        raise SchematisationError(
            f"Incorrect timeseries format for lateral 2D with id: {lateral_2d.id}"
        )

    offset = values[0][0]

    if offset > 0:
        # Shift timeseries to start at t=0
        values = [[x[0] - offset, x[1]] for x in values]

    # x,y is correct (4.294348493375471, 52.033176579129936) until we alter the API
    point = json.loads(session.scalar(lateral_2d.the_geom.ST_AsGeoJSON()))

    return Lateral(
        offset=int(values[0][0]),
        values=values,
        point=point,
        units="m3/s",
        interpolate=False,
    )


class LateralsExtractor(object):
    def __init__(self, session: Session):
        self.session = session
        self._laterals_2d = None
        self._laterals_1d = None

    @property
    def laterals_2d(self) -> List[Lateral]:
        if self._laterals_2d is None:
            laterals_2d = Query(Lateral2D).with_session(self.session).all()
            self._laterals_2d = [
                lateral_2d_to_api_lateral(x, self.session) for x in laterals_2d
            ]

        return self._laterals_2d

    @property
    def laterals_1d(self) -> List[Lateral]:
        if self._laterals_1d is None:
            laterals_1d = Query(Lateral1d).with_session(self.session).all()
            self._laterals_1d = [lateral_1d_to_api_lateral(x) for x in laterals_1d]

        return self._laterals_1d

    def all_laterals(self) -> List[Lateral]:
        return self.laterals_2d + self.laterals_1d

    def as_list(self) -> List[dict]:
        json_laterals = []
        for lateral in self.all_laterals():
            json_lateral = lateral.to_dict()
            strip_dict_none_values(json_lateral)
            json_laterals.append(json_lateral)
        return json_laterals
