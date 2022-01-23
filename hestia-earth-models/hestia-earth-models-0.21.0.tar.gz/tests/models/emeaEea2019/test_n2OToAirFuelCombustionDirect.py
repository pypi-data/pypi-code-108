from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.emeaEea2019.n2OToAirFuelCombustionDirect import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.emeaEea2019.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/emeaEea2019/{TERM_ID}"
TERMS = [
    'diesel'
]


@patch(f"{class_path}._get_fuel_values")
def test_should_run(mock_get_fuel_values):
    # no fuel values => no run
    mock_get_fuel_values.return_value = ([], [])
    should_run, *args = _should_run({})
    assert not should_run

    # with fuel values => run
    mock_get_fuel_values.return_value = ([0], [0])
    should_run, *args = _should_run({})
    assert should_run is True

    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch('hestia_earth.models.emeaEea2019.utils.get_liquid_fuel_terms', return_value=TERMS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch('hestia_earth.models.emeaEea2019.utils.get_liquid_fuel_terms', return_value=TERMS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_data_complete(*args):
    with open(f"{fixtures_folder}/no-input-data-complete/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/no-input-data-complete/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
