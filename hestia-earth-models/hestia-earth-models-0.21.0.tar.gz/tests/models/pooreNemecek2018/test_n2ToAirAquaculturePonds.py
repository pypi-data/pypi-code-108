from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.pooreNemecek2018.n2ToAirAquaculturePonds import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.is_model_enabled", return_value=False)
@patch(f"{class_path}.total_excreta_n", return_value=0)
@patch(f"{class_path}.total_excreta_tan", return_value=0)
def test_should_run(mock_total_excreta_n, mock_total_excreta_tan, mock_is_model_enabled, *args):
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # model enabled => no run
    mock_is_model_enabled.return_value = True
    should_run, *args = _should_run(cycle)
    assert not should_run

    # without neither n nor tan => no run
    mock_total_excreta_n.return_value = 0
    mock_total_excreta_tan.return_value = 0
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with n but no tan => run
    mock_total_excreta_n.return_value = 10
    mock_total_excreta_tan.return_value = 0
    should_run, *args = _should_run(cycle)
    assert should_run is True

    # with tan but no n => run
    mock_total_excreta_n.return_value = 0
    mock_total_excreta_tan.return_value = 10
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
