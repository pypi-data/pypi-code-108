import pandas as pd
import pytest

from preheat_open import test


class TestBuilding(test.PreheatTest):
    def test_load_data(self, unit_with_data, short_period):
        assert unit_with_data is not None
        assert unit_with_data.data is not None
        assert not unit_with_data.data.empty
        assert unit_with_data.has_data()
        print(unit_with_data.data)
        assert unit_with_data.has_data("supplyT")
        with pytest.warns(RuntimeWarning):
            unit_with_data.load_data(*short_period)
            assert not unit_with_data.data.empty

    def test_clear_data(self, unit_with_data):
        unit_with_data.clear_data()
        assert unit_with_data.data is not None
        assert unit_with_data.data.empty

    def test_selected_data_loading(self, unit, short_period):
        unit.load_data(*short_period, components=["energy", "power"])
        assert unit.data is not None
        assert not unit.data.empty
        assert "energy" in unit.data.keys()
        assert "power" in unit.data.keys()
        assert "volume" not in unit.data.keys()
        assert "supplyT" not in unit.data.keys()

    def test_get_state(self, unit, short_period):
        s = unit.get_state(update=True, estimate="last", seconds_back=300)
        # The location does not get new data
        assert len(s) == 0
        # retrieve old state
        t_now = short_period[0]
        s = unit.get_state(update=True, estimate="last", seconds_back=300, t_now=t_now)
        assert len(s) > 0
        unit.clear_state()
