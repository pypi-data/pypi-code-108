from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.emeaEea2019.nh3ToAirExcreta import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.find_primary_product", return_value={'term': {'@id': 'product'}})
@patch(f"{class_path}._is_term_type_complete", return_value=False)
@patch(f"{class_path}.total_excreta_tan", return_value=None)
@patch(f"{class_path}.get_nh3_factor", return_value=None)
def test_should_run(mock_get_lookup_factor, mock_excreta, mock_is_complete, *args):
    # no practice factor => no run
    should_run, *args = _should_run({})
    assert not should_run

    # no excreta => no run
    mock_get_lookup_factor.return_value = 10
    should_run, *args = _should_run({})
    assert not should_run

    # with excretaKgN => run
    mock_excreta.return_value = 10
    should_run, *args = _should_run({})
    assert should_run is True

    # with 0 NH3-N EF => run
    mock_get_lookup_factor.return_value = 0
    mock_excreta.return_value = 10
    should_run, *args = _should_run({})
    assert should_run is True

    # with no NH3-N EF => no run
    mock_get_lookup_factor.return_value = None
    mock_excreta.return_value = 10
    should_run, *args = _should_run({})
    assert not should_run

    # is complete => run
    mock_is_complete.return_value = True
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
