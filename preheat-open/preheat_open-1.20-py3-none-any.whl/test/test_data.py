import pandas as pd

import preheat_open.data
from preheat_open import test
from preheat_open.helpers import sanitise_datetime_input

START_DATE = sanitise_datetime_input("2021-05-01 00:00:00+02:00")
END_DATE = sanitise_datetime_input("2021-05-07 00:00:00+02:00")
COMPONENT_MAP = {
    "32618": "supplyT",
    "32621": "returnT",
    "32622": "flow",
    "32619": "volume",
    "32617": "energy",
    "32620": "power",
}
COMPONENT_MAP_BOX = {"1062545": "x", "1062544": "y"}
COMPONENT_MAP_WEATHER = {
    "18": "Temperature",
    "19": "Humidity",
    "20": "WindDirection",
    "21": "WindSpeed",
    "22": "Pressure",
    "23": "LowClouds",
    "24": "MediumClouds",
    "25": "HighClouds",
    "26": "Fog",
    "27": "WindGust",
    "28": "DewPointTemperature",
    "29": "Cloudiness",
    "30": "Precipitation",
    "31": "DirectSunPower",
    "32": "DiffuseSunPower",
    "33": "SunAltitude",
    "34": "SunAzimuth",
    "35": "DirectSunPowerVertical",
}
TIME_RESOLUTION = "hour"


class TestData(test.PreheatTest):
    def test_json_csv_model(self):
        """
        Test that the new csv format options is equal to the old json
        """
        path = "units/measurements"
        id_key = "ids"

        resp_json = preheat_open.data.perform_requests(
            path,
            id_key,
            list(COMPONENT_MAP.keys()),
            START_DATE,
            END_DATE,
            TIME_RESOLUTION,
            "json",
        )
        data_json = preheat_open.data.extract_data(
            resp_json, "id", COMPONENT_MAP, "json"
        )

        resp_csv = preheat_open.data.perform_requests(
            path,
            id_key,
            list(COMPONENT_MAP.keys()),
            START_DATE,
            END_DATE,
            TIME_RESOLUTION,
            "csv",
        )
        data_csv = preheat_open.data.extract_data(resp_csv, "id", COMPONENT_MAP, "csv")

        assert data_json is not None
        assert data_csv is not None
        assert not data_json.empty
        assert not data_csv.empty
        pd.testing.assert_frame_equal(data_json, data_csv)

    def test_json_csv_box(self):
        """
        Test that the new csv format options is equal to the old json
        """
        path = "measurements"
        id_key = "cids"

        resp_json = preheat_open.data.perform_requests(
            path,
            id_key,
            list(COMPONENT_MAP_BOX.keys()),
            START_DATE,
            END_DATE,
            TIME_RESOLUTION,
            "json",
        )
        data_json = preheat_open.data.extract_data(
            resp_json, "cid", COMPONENT_MAP_BOX, "json"
        )

        resp_csv = preheat_open.data.perform_requests(
            path,
            id_key,
            list(COMPONENT_MAP_BOX.keys()),
            START_DATE,
            END_DATE,
            TIME_RESOLUTION,
            "csv",
        )
        data_csv = preheat_open.data.extract_data(
            resp_csv, "cid", COMPONENT_MAP_BOX, "csv"
        )

        assert data_json is not None
        assert data_csv is not None
        assert not data_json.empty
        assert not data_csv.empty
        pd.testing.assert_frame_equal(data_json, data_csv)

    def test_json_csv_weather(self, building_id):
        """
        Test that the new csv format options is equal to the old json
        """
        path = f"weather/{building_id}"
        id_key = "type_ids"

        resp_json = preheat_open.data.perform_requests(
            path,
            id_key,
            list(COMPONENT_MAP_WEATHER.keys()),
            START_DATE,
            END_DATE,
            TIME_RESOLUTION,
            "json",
        )
        data_json = preheat_open.data.extract_data(
            resp_json, "type_id", COMPONENT_MAP_WEATHER, "json"
        )

        resp_csv = preheat_open.data.perform_requests(
            path,
            id_key,
            list(COMPONENT_MAP_WEATHER.keys()),
            START_DATE,
            END_DATE,
            TIME_RESOLUTION,
            "csv",
        )
        data_csv = preheat_open.data.extract_data(
            resp_csv, "type_id", COMPONENT_MAP_WEATHER, "csv"
        )

        assert data_json is not None
        assert data_csv is not None
        assert not data_json.empty
        assert not data_csv.empty
        pd.testing.assert_frame_equal(data_json, data_csv)

    def test_load_box_data(self):
        df = preheat_open.data.load_box_data(
            COMPONENT_MAP_BOX, START_DATE, END_DATE, TIME_RESOLUTION
        )
        assert df is not None
        assert not df.empty

    def test_load_model_data(self):
        df = preheat_open.data.load_model_data(
            COMPONENT_MAP, START_DATE, END_DATE, TIME_RESOLUTION
        )
        assert df is not None
        assert not df.empty

    def test_load_weather_data(self, building_id):
        df = preheat_open.data.load_weather_data(
            building_id, COMPONENT_MAP_WEATHER, START_DATE, END_DATE, TIME_RESOLUTION
        )
        assert df is not None
        assert not df.empty
