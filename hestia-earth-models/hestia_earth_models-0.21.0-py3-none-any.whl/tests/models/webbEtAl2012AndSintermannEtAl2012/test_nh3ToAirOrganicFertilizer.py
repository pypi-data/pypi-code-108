from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.webbEtAl2012AndSintermannEtAl2012.nh3ToAirOrganicFertilizer import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.webbEtAl2012AndSintermannEtAl2012.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/webbEtAl2012AndSintermannEtAl2012/{TERM_ID}"


@patch(f"{class_path}._get_nitrogen_tan_content", return_value=1)
@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}._is_term_type_complete", return_value=False)
def test_should_run(*args):
    # no inputs => no run
    cycle = {'inputs': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with slurryAndSludgeKgN input => run
    cycle['inputs'].append({
        'term': {
            '@id': 'slurryAndSludgeKgN',
            'termType': 'organicFertilizer',
            'units': 'kg N'
        },
        'value': [100]
    })
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with cattleSolidManureFreshKgN input => no run
    cycle['inputs'].append({
        'term': {
            '@id': 'cattleSolidManureFreshKgN',
            'termType': 'organicFertilizer',
            'units': 'kg N'
        },
        'value': [100]
    })
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with compostKgN input => no run
    cycle['inputs'].append({
        'term': {
            '@id': 'compostKgN',
            'termType': 'organicFertilizer',
            'units': 'kg N'
        },
        'value': [100]
    })
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with greenManureKgN input => run
    cycle['inputs'].append({
        'term': {
            '@id': 'greenManureKgN',
            'termType': 'organicFertilizer',
            'units': 'kg N'
        },
        'value': [100]
    })
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
