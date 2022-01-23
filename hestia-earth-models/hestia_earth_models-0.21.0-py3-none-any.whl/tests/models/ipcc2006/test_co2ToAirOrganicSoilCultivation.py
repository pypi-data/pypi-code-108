import json
from unittest.mock import patch
from hestia_earth.schema import SiteSiteType

from hestia_earth.models.ipcc2006.co2ToAirOrganicSoilCultivation import TERM_ID, _should_run, run
from tests.utils import fake_new_emission, fixtures_path

class_path = f"hestia_earth.models.ipcc2006.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/ipcc2006/{TERM_ID}"


@patch(F"{class_path}.find_primary_product", return_value={'@id': 'product'})
@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.land_occupation_per_kg", return_value=10)
@patch(f"{class_path}.most_relevant_measurement_value", return_value=0)
def test_should_run(mock_measurement, *args):
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    mock_measurement.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    cycle = {"site": {"siteType": SiteSiteType.CROPLAND.value}}
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_pasture(*args):
    with open(f"{fixtures_folder}/pasture/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/pasture/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
