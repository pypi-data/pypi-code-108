from enum import Enum
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session
from threedi_modelchecker.simulation_templates.exceptions import (
    SchematisationError,
)
from threedi_modelchecker.simulation_templates.utils import parse_timeseries
from threedi_modelchecker.threedi_model.models import BoundaryCondition1D
from threedi_modelchecker.threedi_model.models import BoundaryConditions2D
from typing import Dict
from typing import List
from typing import Union


# JSON format example:
# [
#     {
#         "id": 1,  (spatialite id from boundary table)
#         "type": "2D"
#         "interpolate": true,
#         "values": [
#             [0, 0.5],
#             [500, 0,8],
#             [1000, 0]
#         ]
#     },
#     {
#         "id": 2, (spatialite id from boundary table)
#         "type": "1D",
#         "interpolate": true,
#         "values": [
#             [0, 0,3],
#             [400, 0.1]
#         ]
#     },
#     {
#         "id": 3, (spatialite id from boundary table)
#         "type": "1D",
#         "interpolate": true,
#         "values": [
#             [0, -2.4],
#             [1300, 0,3],
#             [3000, 1.2],
#             [3600, 0]
#         ]
#     }
# ]


class BoundaryType(Enum):
    one_d = "1D"
    two_d = "2D"


def sqlite_boundary_to_dict(
    boundary: Union[BoundaryConditions2D, BoundaryCondition1D]
) -> Dict:

    boundary_1d2d: BoundaryType = BoundaryType.one_d
    if isinstance(boundary, BoundaryConditions2D):
        boundary_1d2d = BoundaryType.two_d

    try:
        values = parse_timeseries(boundary.timeseries)
    except (TypeError, ValueError):
        raise SchematisationError(
            f"Incorrect formatted timeseries for {boundary_1d2d.value} boundary condition with id={boundary.id}"
        )

    return {
        "id": boundary.id,
        "type": boundary_1d2d.value,
        "interpolate": True,
        "values": values,
    }


class BoundariesExtractor(object):
    def __init__(self, session: Session):
        self.session = session
        self._boundaries_2d = None
        self._boundaries_1d = None

    @property
    def boundaries_2d(self) -> List[Dict]:
        if self._boundaries_2d is None:
            boundaries_2d = (
                Query(BoundaryConditions2D)
                .with_session(self.session)
                .order_by(BoundaryConditions2D.id)
                .all()
            )

            self._boundaries_2d = [sqlite_boundary_to_dict(x) for x in boundaries_2d]

        return self._boundaries_2d

    @property
    def boundaries_1d(self) -> List[Dict]:
        if self._boundaries_1d is None:
            boundaries_1d = (
                Query(BoundaryCondition1D)
                .with_session(self.session)
                .order_by(BoundaryCondition1D.id)
                .all()
            )
            self._boundaries_1d = [sqlite_boundary_to_dict(x) for x in boundaries_1d]

        return self._boundaries_1d

    def as_list(self) -> List[Dict]:
        """
        Returns: list with dict's for every boundary, 2d boundaries before 1d boundaries
        """
        return self.boundaries_2d + self.boundaries_1d
