from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.stehfestBouwman2006GisImplementation.noxToAirSoilFlux import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.stehfestBouwman2006GisImplementation.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/stehfestBouwman2006GisImplementation/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.residue_nitrogen", return_value=0)
def test_should_run(*args):
    # no country => no run
    cycle = {'inputs': [], 'site': {}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with country => no run
    cycle['site'] = {'country': {'@id': 'country'}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with kg N inputs => run
    cycle['inputs'] = [{
        'term': {
            'units': 'kg N'
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
