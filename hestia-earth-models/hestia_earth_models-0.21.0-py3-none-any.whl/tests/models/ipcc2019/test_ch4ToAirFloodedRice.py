from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission, FLOODED_RICE_TERMS

from hestia_earth.models.ipcc2019.ch4ToAirFloodedRice import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.has_flooded_rice", return_value=False)
def test_should_run(mock_flooded_rice):
    # no site => no run
    cycle = {'site': {}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with site => no run
    cycle['site'] = {'country': {'@id': 'country'}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with croppingDuration => no run
    cycle['practices'] = [{'term': {'@id': 'croppingDuration'}}]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with flooded rice => run
    mock_flooded_rice.return_value = True
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch('hestia_earth.models.utils.product.get_rice_paddy_terms', return_value=FLOODED_RICE_TERMS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch('hestia_earth.models.utils.product.get_rice_paddy_terms', return_value=FLOODED_RICE_TERMS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_optional_data(*args):
    with open(f"{fixtures_folder}/with-optional-data/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-optional-data/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
