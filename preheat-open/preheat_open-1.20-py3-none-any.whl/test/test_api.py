import datetime

import pandas as pd

from preheat_open import test
from preheat_open.api import (
    ApiSession,
    api_get,
    api_put,
    api_string_to_datetime,
    datetime_to_api_string,
    ids_list_to_string,
)


class TestApi(test.PreheatTest):
    def test_load_api_key(self):
        api_key = ApiSession().get_api_key()
        assert len(api_key) > len("Apikey ")
        assert api_key == "Apikey " + test.API_KEY

    def test_api_string_to_datetime(self):
        dt = api_string_to_datetime("2021-05-11T08:09:13.370Z")
        assert isinstance(dt, datetime.datetime)
        assert dt.year == 2021
        assert dt.month == 5
        assert dt.day == 11
        assert dt.hour == 8
        assert dt.minute == 9
        assert dt.second == 13
        assert dt.microsecond == 370000
        assert str(dt.tzinfo) == "UTC"

        dt = api_string_to_datetime("2020-04-10T07:08:12.369+02:00")
        assert isinstance(dt, datetime.datetime)
        assert dt.year == 2020
        assert dt.month == 4
        assert dt.day == 10
        assert dt.hour == 7
        assert dt.minute == 8
        assert dt.second == 12
        assert dt.microsecond == 369000
        assert str(dt.tzinfo) == "UTC+02:00"

    def test_datetime_to_api_string(self):
        dt = api_string_to_datetime("2021-05-11T08:09:13.370Z")
        assert datetime_to_api_string(dt) == "2021-05-11T08:09:13.370000+00:00"

        dt = api_string_to_datetime("2020-04-10T07:08:12.369+02:00")
        assert datetime_to_api_string(dt) == "2020-04-10T07:08:12.369000+02:00"

    def test_api_get(self, building_id):
        response = api_get(f"locations/{building_id}")
        assert response is not None
        assert "building" in response

    def test_api_put(self, control_unit_id):
        payload = {
            "schedule": [
                {
                    "startTime": "2020-01-01T00:00:00+02:00",
                    "value": 1,
                    "operation": "NORMAL",
                },
                {
                    "startTime": "2020-01-01T00:01:00+02:00",
                    "value": 0,
                    "operation": "NORMAL",
                },
                {
                    "startTime": "2020-01-01T00:02:00+02:00",
                    "value": 1,
                    "operation": "NORMAL",
                },
                {
                    "startTime": "2020-01-01T00:03:00+02:00",
                    "value": 0,
                    "operation": "NORMAL",
                },
                {
                    "startTime": "2020-01-01T00:04:00+02:00",
                    "value": 1,
                    "operation": "NORMAL",
                },
                {
                    "startTime": "2020-01-01T00:05:00+02:00",
                    "value": 0,
                    "operation": "NORMAL",
                },
            ]
        }
        response = api_put(f"controlunit/{control_unit_id}/setpoint", payload)
        pass

    def test_ids_list_to_string(self):
        assert ids_list_to_string([1, 2, 3], separator=",") == "1,2,3"
        assert ids_list_to_string([1, 2, 3], separator=";") == "1;2;3"
        assert ids_list_to_string(pd.Series([1, 2, 3]), separator=",") == "1,2,3"
        assert (
            ids_list_to_string(pd.Series([1, 2, 3]).to_numpy(), separator=",")
            == "1,2,3"
        )
