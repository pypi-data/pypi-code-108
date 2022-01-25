import warnings

import pytest

import preheat_open
from preheat_open import running_in_test_mode

# Setting up a test API key, which is only valid for a dummy test installation
API_KEY = "KVkIdWLKac5XFLCs2loKb7GUitkTL4uJXoSyUFIZkVgWuCk8Uj"
ANONYMISED_API_KEY = "3xa0SeGXa4WlkrB68qGR9NoDAzVvGdiG3XAabKu6n7n5qQTDkL"

# Warning the user that this module is not meant to be used for non test-related activities
if running_in_test_mode() is False:
    warnings.warn(
        """

The module 'preheat_open.test' is not meant to be imported and actively used, 
unless you are specifically carrying out a test.

    """
    )

SHORT_TEST_PERIOD = ("2021-05-01 00:00", "2021-05-02 00:00", "hour")


class PreheatTest:
    @pytest.fixture(autouse=True)
    def set_api_key(self):
        preheat_open.api.set_api_key(API_KEY)

    @pytest.fixture()
    def bypass_api_key(self):
        preheat_open.api.set_api_key(None)
        yield None
        preheat_open.api.set_api_key(API_KEY)

    @pytest.fixture()
    def building_id(self):
        return 2756

    @pytest.fixture()
    def unit_id(self):
        return 15312

    @pytest.fixture()
    def control_unit_id(self):
        return 15357

    @pytest.fixture()
    def building(self, building_id):
        return preheat_open.Building(building_id)

    @pytest.fixture()
    def building_with_data(self, building, medium_period):
        building.load_data(*medium_period)
        yield building
        building.clear_data()

    @pytest.fixture()
    def unit(self, building, unit_id):
        return building.query_units(unit_id=unit_id)[0]

    @pytest.fixture()
    def unit_with_data(self, unit, medium_period):
        unit.load_data(*medium_period)
        yield unit
        unit.clear_data()

    @pytest.fixture()
    def control_unit(self, building):
        return building.qu("control", "control_unit_custom_1")

    @pytest.fixture()
    def weather_unit(self, building):
        return building.weather

    @pytest.fixture()
    def short_period(self):
        start_date = SHORT_TEST_PERIOD[0]
        end_date = SHORT_TEST_PERIOD[1]
        time_resolution = "hour"
        return start_date, end_date, time_resolution

    @pytest.fixture()
    def medium_period(self):
        start_date = "2021-05-01 00:00"
        end_date = "2021-05-07 00:00"
        time_resolution = "hour"
        return start_date, end_date, time_resolution
