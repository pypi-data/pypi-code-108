import numpy as np
import pandas as pd
from requests.models import Response

from .building_unit import BaseBuildingUnit
from .logging import Logging
from .setpoints import get_setpoint_schedule, send_setpoint_schedule


class ControlUnit(BaseBuildingUnit):
    """Control Unit; an extension of Unit to handle controls"""

    def __init__(self, unit_data, building_ref=None):
        super().__init__("control", unit_data, building_ref)
        if "active" in unit_data.keys():
            self.active = unit_data["active"]
        else:
            self.active = False

    def request_schedule(self, schedule_df) -> Response:
        if self.active is False:
            Logging().warning(
                """Warning: you are trying to control an unit that is not activated 
                (id={} / details: [unit: {} / building: [{}] {}])""".format(
                    self.id,
                    self.name,
                    self.building.location["locationId"],
                    self.building.location["address"],
                )
            )
        if schedule_df["value"].isnull().any():
            raise ValueError("requested schedule has missing values")
        if np.isinf(schedule_df["value"]).any():
            raise ValueError("requested schedule has infinite values")
        return send_setpoint_schedule(self.id, schedule_df)

    def get_schedule(self, start_date, end_date) -> pd.DataFrame:
        return get_setpoint_schedule(self.id, start_date, end_date)
