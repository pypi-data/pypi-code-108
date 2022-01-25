from preheat_open import test
from preheat_open.helpers import now, timedelta


class TestPrice(test.PreheatTest):
    def test_building(self, building):
        assert building is not None

        sps = building.get_supply_points()
        assert sps is not None, "Failure in supply points"

        comps = sps[0].get_price_components()
        assert comps is not None, "Failure in price components extraction"

        sps[0].load_price_data(start_time=now() - timedelta(days=1), end_time=now())
        data, T = sps[0].get_price_data()

        print(T)
        print(data)

        assert data is not None, "Failure in data"
        assert T is not None, "Failure in data labelling"
