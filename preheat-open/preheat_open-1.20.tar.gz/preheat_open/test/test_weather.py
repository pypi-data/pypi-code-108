import pandas as pd
import pytest

from preheat_open import test


class TestBuilding(test.PreheatTest):
    def test_load_data(self, weather_unit, short_period):
        weather_unit.load_data(*short_period)
        assert weather_unit is not None
        assert weather_unit.data is not None
        assert not weather_unit.data.empty
        assert weather_unit.has_data()
        print(weather_unit.data)
        assert weather_unit.has_data("Temperature")
        with pytest.warns(RuntimeWarning):
            weather_unit.load_data(*short_period)
            assert not weather_unit.data.empty

    def test_clear_data(self, weather_unit, short_period):
        weather_unit.load_data(*short_period)
        weather_unit.clear_data()
        assert weather_unit.data is not None
        assert weather_unit.data.empty

    def test_selected_data_loading(self, weather_unit, unit, short_period):
        weather_unit.load_data(*short_period, components=["Temperature", "LowClouds"])
        assert weather_unit.data is not None
        assert not weather_unit.data.empty
        assert "Temperature" in weather_unit.data.keys()
        assert "LowClouds" in weather_unit.data.keys()
        assert "Humidity" not in weather_unit.data.keys()
        assert "Fog" not in weather_unit.data.keys()

    def test_get_state(self, weather_unit):

        sw1 = weather_unit.get_state(
            update=True, estimate="last", seconds_back=12 * 3600
        )
        sw2 = weather_unit.get_state(update=False, estimate="median")
        sw3 = weather_unit.get_state(update=False, estimate="mean")
        assert isinstance(sw1, pd.Series)
        assert isinstance(sw2, pd.Series)
        assert isinstance(sw3, pd.Series)

        # The location does not get new data
        assert len(sw1) > 0
        assert len(sw2) > 0
        assert len(sw3) > 0
        weather_unit.clear_state()
