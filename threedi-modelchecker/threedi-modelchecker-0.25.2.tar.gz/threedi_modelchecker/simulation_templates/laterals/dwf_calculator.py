from threedi_modelchecker.threedi_model.constants import InflowType
from sqlalchemy.orm import Session
from typing import Dict
from typing import List
from typing import Optional
from typing import Union


INFLOW_TABLE_NAME_BASES = {
    InflowType.IMPERVIOUS_SURFACE: "impervious_surface",
    InflowType.SURFACE: "surface",
}


# Default values
DWF_FACTORS = [
    [0, 0.03],
    [1, 0.015],
    [2, 0.01],
    [3, 0.01],
    [4, 0.005],
    [5, 0.005],
    [6, 0.025],
    [7, 0.080],
    [8, 0.075],
    [9, 0.06],
    [10, 0.055],
    [11, 0.05],
    [12, 0.045],
    [13, 0.04],
    [14, 0.04],
    [15, 0.035],
    [16, 0.035],
    [17, 0.04],
    [18, 0.055],
    [19, 0.08],
    [20, 0.07],
    [21, 0.055],
    [22, 0.045],
    [23, 0.04],
    [24, 0.0],  # Timeseries for laterals should contain 25 values
]


def read_dwf_per_node(
    session: Session, inflow_type: InflowType
) -> List[Union[int, float]]:
    """Obtains the total dry weather flow in m3/d per connection node from a 3Di model sqlite-file."""

    basename = INFLOW_TABLE_NAME_BASES[inflow_type]
    query = f"""
        SELECT 	map.connection_node_id,
                sum(surf.dry_weather_flow * surf.nr_of_inhabitants * map.percentage/100)/1000 AS dwf
        FROM 	v2_{basename} AS surf
        JOIN 	v2_{basename}_map AS map
        ON 		surf.id = map.{basename}_id
        WHERE 	surf.dry_weather_flow IS NOT NULL
                and surf.nr_of_inhabitants != 0
                and surf.nr_of_inhabitants IS NOT NULL
                and map.percentage IS NOT NULL
        GROUP BY map.connection_node_id
    """
    dwf_per_node = [
        [connection_node_id, weighted_flow_sum]
        for connection_node_id, weighted_flow_sum in session.execute(query)
    ]

    return dwf_per_node


def generate_dwf_laterals(session: Session, inflow_type: InflowType) -> List[Dict]:
    """Generate dry weather flow laterals from spatialite """
    dwf_per_node = read_dwf_per_node(session, inflow_type)
    dwf_laterals = []

    # Generate lateral for each connection node
    for node_id, flow in dwf_per_node:
        values = [[hour * 3600, flow * factor / 3600] for hour, factor in DWF_FACTORS]
        dwf_laterals.append(
            dict(
                offset=0,
                values=values,
                units="m3/s",
                connection_node=node_id,
                interpolate=False,
            )
        )

    return dwf_laterals


class DWFCalculator:
    """Calculate dry weather flow (DWF) from sqlite."""

    def __init__(self, session: Session, inflow_type: InflowType) -> None:
        self.session = session
        self.inflow_type = inflow_type
        self._laterals = None

    @property
    def laterals(self) -> List[Optional[Dict]]:
        if self.inflow_type not in [InflowType.SURFACE, InflowType.IMPERVIOUS_SURFACE]:
            return []

        if self._laterals is None:
            self._laterals = generate_dwf_laterals(self.session, self.inflow_type)

        return self._laterals
