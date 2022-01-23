from unittest.mock import patch
import json

from hestia_earth.schema import TermTermType
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.ipcc2019.nitrogenContent import (
    MODEL, TERM_ID, run, _should_run, _should_run_product, _should_run_multiple_crop_product
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._should_run_product", return_value=True)
@patch(f"{class_path}._should_run_single_crop_product", return_value=False)
@patch(f"{class_path}._should_run_multiple_crop_product", return_value=False)
def test_should_run(mock_should_run_multiple, mock_should_run_single, *args):
    crop_product = {'term': {'termType': TermTermType.CROP.value}}
    cycle = {'products': []}

    # with a single crop => no run
    cycle['products'] = [crop_product]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # allowing single product => run
    mock_should_run_single.return_value = True
    should_run, *args = _should_run(cycle)
    assert should_run is True

    # with multiple crops => no run
    cycle['products'] = [crop_product, crop_product]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # allowing multiple products => run
    mock_should_run_multiple.return_value = True
    should_run, *args = _should_run(cycle)
    assert should_run is True


def test_should_run_product():
    product = {}

    # not a runed product => no run
    product['term'] = {'@id': 'random id'}
    assert not _should_run_product(product)

    # with a runed product => run
    product['term']['@id'] = 'aboveGroundCropResidueTotal'
    assert _should_run_product(product) is True

    prop = {
        'term': {
            '@id': TERM_ID
        }
    }
    product['properties'] = [prop]
    assert not _should_run_product(product)


@patch(f"{class_path}._get_crop_value", return_value=None)
def test_should_run_multiple_crop_product(mock_get_crop_value):
    product = {'term': {'@id': 'maizeGrain'}}

    # with a dryMatter property => no run
    product['properties'] = [{'term': {'@id': 'dryMatter'}, 'value': 10}]
    assert not _should_run_multiple_crop_product(product)

    # with a value => no run
    product['value'] = [10]
    assert not _should_run_multiple_crop_product(product)

    # with a lookup value => run
    mock_get_crop_value.return_value = 10
    assert _should_run_multiple_crop_product(product) is True


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run_single_crop(*args):
    with open(f"{fixtures_folder}/single-crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/single-crop/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run_multiple_crops(*args):
    with open(f"{fixtures_folder}/multiple-crops/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/multiple-crops/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run_multiple_crops_single_residue(*args):
    with open(f"{fixtures_folder}/multiple-crops-single-residue/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/multiple-crops-single-residue/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
