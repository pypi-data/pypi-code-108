from unittest.mock import patch
import json

from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.faostat2018.carcassWeightPerHead import MODEL, TERM_ID, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
FAO_TERM = {
    '@id': 'meatChickenReadyToCookWeight',
    '@type': 'Term',
    'units': 'kg ready-to-cook weight',
    'defaultProperties': [{
        'term': {'@id': 'processingConversionCarcassWeightToReadyToCookWeight'},
        'value': 72.45065789473684
    }]
}


def test_should_run():
    cycle = {}

    # no animal products => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with animal products => no run
    cycle['products'] = [
        {
            'term': {
                'termType': TermTermType.ANIMALPRODUCT.value,
                'units': 'kg carcass weight'
            }
        }
    ]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with an endDate and country => run
    cycle['endDate'] = '2020'
    cycle['site'] = {'country': {'@id': 'GADM-GBR'}}
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"hestia_earth.models.{MODEL}.utils.download_hestia", return_value=FAO_TERM)
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
