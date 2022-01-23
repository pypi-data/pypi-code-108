from unittest.mock import patch
import json

from hestia_earth.schema import SiteSiteType

from tests.utils import fixtures_path, fake_new_emission
from hestia_earth.models.pooreNemecek2018.ch4ToAirAquaculturePonds import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.most_relevant_measurement_value", return_value=10)
@patch(f"{class_path}.is_model_enabled", return_value=False)
@patch(F"{class_path}.find_term_match", return_value={})
def test_should_run(mock_find_term, mock_is_model_enabled, *args):
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # model enabled => no run
    mock_is_model_enabled.return_value = True
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with kg Vs product => no run
    cycle['products'] = [
        {
            'term': {
                'units': 'kg VS',
                'termType': 'excreta'
            },
            'value': [
                2.17651622575813
            ]
        }
    ]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with a siteType => no run
    cycle['site'] = {'siteType': SiteSiteType.SEA_OR_OCEAN.value}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with all measurements and practices => run
    mock_find_term.return_value = {'value': [10]}
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_cropland(*args):
    with open(f"{fixtures_folder}/with-cropland/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-cropland/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_marine(*args):
    with open(f"{fixtures_folder}/with-marine/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-marine/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
