import datetime

import numpy as np
import pandas as pd
import pytest
from requests.models import Response

from preheat_open import test
from preheat_open.helpers import sanitise_datetime_input


class TestControlUnit(test.PreheatTest):
    def test_query(self, control_unit):
        assert control_unit is not None

    def test_get_schedule(self, control_unit):
        start_time = "2020-01-01T00:00:00+02:00"
        end_time = "2020-01-01T12:00:00+02:00"
        schedule_data = control_unit.get_schedule(start_time, end_time)
        assert schedule_data is not None
        assert not schedule_data.empty

        start_time = "1970-06-01T00:00:00+02:00"
        end_time = "1970-06-01T12:00:00+02:00"
        schedule_data = control_unit.get_schedule(start_time, end_time)
        assert schedule_data is not None
        assert schedule_data.empty

    def test_request_schedule(self, control_unit):
        start_time = sanitise_datetime_input("2020-01-01T00:00:00+02:00")
        end_time = sanitise_datetime_input("2020-01-01T00:05:00+02:00")

        with pytest.warns(UserWarning):
            response = self.send_schedule(
                control_unit, start_time, end_time, 1, 0, 1, 0, 1, 0
            )
            assert response.status_code == 200
            schedule = control_unit.get_schedule(
                start_time, end_time + datetime.timedelta(seconds=1)
            )  # type: pd.DataFrame
            self.check_schedule(schedule, 1, 0, 1, 0, 1, 0)

            response = self.send_schedule(
                control_unit, start_time, end_time, 0, 1, 0, 1, 0, 1
            )
            assert response.status_code == 200
            schedule = control_unit.get_schedule(
                start_time, end_time + datetime.timedelta(seconds=1)
            )
            self.check_schedule(schedule, 0, 1, 0, 1, 0, 1)

            response = self.send_schedule_without_mode(
                control_unit, start_time, end_time, 0, 1, 0, 1, 0, 2
            )
            assert response.status_code == 200
            schedule = control_unit.get_schedule(
                start_time, end_time + datetime.timedelta(seconds=1)
            )
            self.check_schedule(schedule, 0, 1, 0, 1, 0, 2)

        # Check raises missing values
        with pytest.raises(Exception):
            self.send_schedule(control_unit, start_time, end_time, 0, np.nan)

        # Check raises infinite values
        with pytest.raises(Exception):
            self.send_schedule(control_unit, start_time, end_time, 0, +np.nan)

        # Check raises negative infinite values
        with pytest.raises(Exception):
            self.send_schedule(control_unit, start_time, end_time, 0, -np.inf)

    def check_schedule(self, schedule, *values):
        assert schedule is not None
        assert schedule.values is not None
        assert len(schedule.values) == len(values)
        for x, y in zip(schedule.values, values):
            assert x[0] == y

    def send_schedule(self, control_unit, start_time, end_time, *values) -> Response:
        t_range = pd.date_range(start_time, end_time, len(values))
        start_times = [pd.to_datetime(t) for t in t_range]
        schedule = {
            "value": values,
            "startTime": start_times,
            "operation": len(values) * ["NORMAL"],
        }
        new_schedule = pd.DataFrame(schedule)
        new_schedule.set_index("startTime", inplace=True)
        return control_unit.request_schedule(new_schedule)  # type: Response

    def send_schedule_without_mode(
        self, control_unit, start_time, end_time, *values
    ) -> Response:
        t_range = pd.date_range(start_time, end_time, len(values))
        start_times = [pd.to_datetime(t) for t in t_range]
        schedule = {
            "value": values,
            "startTime": start_times,
        }
        new_schedule = pd.DataFrame(schedule)
        new_schedule.set_index("startTime", inplace=True)
        return control_unit.request_schedule(new_schedule)  # type: Response

    def test_get_zones(self, control_unit):
        from preheat_open.building_unit import BuildingUnit
        from preheat_open.zone import Zone

        z_A1 = control_unit.get_zones()
        pars = control_unit.parents()
        assert len(z_A1) == 1
        assert isinstance(z_A1[0], Zone)
        assert z_A1[0].name == "Zone_A1"
        assert len(pars) == 1
        assert isinstance(pars[0], BuildingUnit)
