from unittest.mock import patch
import json
from hestia_earth.schema import CycleFunctionalUnit
from tests.utils import fixtures_path, fake_new_property, fake_download

from hestia_earth.models.globalCropWaterModel2008.rootingDepth import TERM_ID, run, _should_run, _should_run_product

class_path = 'hestia_earth.models.globalCropWaterModel2008.rootingDepth'
fixtures_folder = f"{fixtures_path}/globalCropWaterModel2008/{TERM_ID}"
TERMS = [
    'waterPumpedGroundwater',
    'waterBrackish',
    'waterSourceUnspecified'
]


@patch(f"{class_path}.valid_site_type", return_value=True)
def test_should_run(*args):
    cycle = {'functionalUnit': CycleFunctionalUnit._1_HA.value}
    assert _should_run(cycle) is True

    cycle = {'functionalUnit': CycleFunctionalUnit.RELATIVE.value}
    assert not _should_run(cycle)


def test_should_run_product():
    product = {}
    # no properties => run
    assert _should_run_product(product) is True

    # product with model => does not run
    prop = {
        'term': {
            '@id': TERM_ID
        }
    }
    product['properties'] = [prop]
    assert not _should_run_product(product)


@patch(f"{class_path}.get_irrigation_terms", return_value=TERMS)
@patch(f"{class_path}.download_hestia", side_effect=fake_download)
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_irrigation_terms", return_value=TERMS)
@patch(f"{class_path}.download_hestia", side_effect=fake_download)
@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_gap_fill_with_irrigation(*args):
    with open(f"{fixtures_folder}/with-irrigation/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-irrigation/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
