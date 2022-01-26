from sqlalchemy.orm import Session
from typing import Dict
from typing import List
from typing import Union


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


def read_dwf_per_node(session: Session) -> List[Union[int, float]]:
    """Obtains the DWF per connection node per second a 3Di model sqlite-file."""

    # Group dry_weather_flow * nr_of_inhabitants per connection node id
    query = """
        SELECT 	ism.connection_node_id,
                sum(isu.dry_weather_flow * isu.nr_of_inhabitants * ism.percentage/100)/1000 AS dwf
        FROM 	v2_impervious_surface isu
        JOIN 	v2_impervious_surface_map ism
        ON 		isu.id = ism.impervious_surface_id
        WHERE 	isu.dry_weather_flow IS NOT NULL
                and isu.nr_of_inhabitants != 0
                and isu.nr_of_inhabitants IS NOT NULL
                and ism.percentage IS NOT NULL
        GROUP BY ism.connection_node_id
    """
    dwf_per_node = [
        [connection_node_id, weighted_flow_sum]
        for connection_node_id, weighted_flow_sum in session.execute(query)
    ]

    return dwf_per_node


def generate_dwf_laterals(session: Session) -> List[Dict]:
    """Generate dry weather flow laterals from spatialite """
    dwf_per_node = read_dwf_per_node(session)
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

    def __init__(self, session: Session) -> None:
        self.session = session
        self._laterals = None

    @property
    def laterals(self) -> List[Dict]:
        if self._laterals is None:
            self._laterals = generate_dwf_laterals(self.session)

        return self._laterals
