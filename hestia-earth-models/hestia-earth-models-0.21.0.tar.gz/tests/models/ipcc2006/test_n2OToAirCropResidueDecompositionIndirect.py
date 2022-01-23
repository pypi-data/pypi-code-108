from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2006.n2OToAirCropResidueDecompositionIndirect import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_should_run(mock_is_complete, *args):
    # no emissions => no run
    cycle = {'emissions': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # is complete => run
    mock_is_complete.return_value = True
    should_run, *args = _should_run(cycle)
    assert should_run is True

    # with no3 emission => run
    cycle['emissions'] = [{
        'term': {
            '@id': 'no3ToGroundwaterCropResidueDecomposition'
        },
        'value': [100]
    }]
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
