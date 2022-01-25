from preheat_open import test


class TestBuildingUnit(test.PreheatTest):
    def test_class(self, unit_with_data):
        assert unit_with_data.is_shared() is False

    def test_load_data(self, unit_with_data):
        assert unit_with_data is not None
        assert unit_with_data.data is not None
        assert not unit_with_data.data.empty
        assert unit_with_data.has_data()
        print(unit_with_data.data)
        assert unit_with_data.has_data("supplyT")

        # TODO add a test of load_data(self, *, load_children=True)
        assert True is True

    def test_clear_data(self, unit_with_data):
        unit_with_data.clear_data()
        assert unit_with_data.data is not None
        assert unit_with_data.data.empty

        unit_with_data.clear_data(clear_children=True)
        assert unit_with_data.data is not None
        assert unit_with_data.data.empty

    def test_get_zones(self, building_with_data):
        from preheat_open.zone import Zone

        zones_ok = building_with_data.qu("indoorClimate").get_zones()
        zones_empty = building_with_data.qu("custom").get_zones()
        assert len(zones_ok) == 1
        assert isinstance(zones_ok[0], Zone)
        assert len(zones_empty) == 0

    def test_query_units(self, building_with_data):
        m = building_with_data.qu("main", unit_id=15312)
        sec = building_with_data.qu("secondaries", unit_id=15401)
        c1 = sec.qu("control", name="dummy_heating_controller")

        assert sec.unit_subtype == "MIXING_LOOP"
        assert m.unit_subtype is None

        assert m.id == sec.qpu("main").id
        assert m.id == c1.qpu("main").id
        assert c1.id == m.qu("control", name="dummy_heating_controller").id
        assert (
            c1.id
            == building_with_data.qu("control", name="dummy_heating_controller").id
        )
