from unittest.mock import patch
import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.economicValueShare import (
    MODEL, MODEL_KEY, run, _should_run_by_product, _should_run_by_revenue, _should_run_single
)

class_path = f"hestia_earth.models.{MODEL}.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/product/{MODEL_KEY}"


def test_should_run_by_revenue():
    # if total value >= 100, do nothing
    products = [{
        '@type': 'Product',
        'economicValueShare': 20
    }, {
        '@type': 'Product',
        'economicValueShare': 80
    }, {
        '@type': 'Product'
    }]
    assert not _should_run_by_revenue({'products': products})

    # total < 100 => no run
    products[1]['economicValueShare'] = 70
    assert not _should_run_by_revenue({'products': products})

    # all with revenue => run
    products[0]['revenue'] = 10
    products[1]['revenue'] = 10
    products[2]['revenue'] = 10
    assert _should_run_by_revenue({'products': products}) is True


@patch(f"{class_path}.find_primary_product")
def test_should_run_by_product(mock_primary_product):
    crop_product = {'term': {'termType': 'crop'}}
    cycle = {'products': [crop_product]}

    # primary product is not crop => no run
    mock_primary_product.return_value = {'term': {'termType': 'liveAnimal'}}
    assert not _should_run_by_product(cycle)

    # primary product is crop => run
    mock_primary_product.return_value = crop_product
    assert _should_run_by_product(cycle) is True

    # multiple crop products => no run
    cycle['products'].append(crop_product)
    assert not _should_run_by_product(cycle)


def test_should_run_single():
    cycle = {'products': []}
    should_run, *args = _should_run_single(cycle)
    assert not should_run

    cycle = {'products': [{}]}
    should_run, *args = _should_run_single(cycle)
    assert should_run is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_no_revenue_single_crop():
    with open(f"{fixtures_folder}/no-revenue-single-crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/no-revenue-single-crop/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_single_product():
    with open(f"{fixtures_folder}/single-product/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/single-product/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
