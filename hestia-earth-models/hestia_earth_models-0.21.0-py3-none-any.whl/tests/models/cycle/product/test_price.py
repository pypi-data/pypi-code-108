import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.price import run, _should_run_product

class_path = 'hestia_earth.models.cycle.product.price'
fixtures_folder = f"{fixtures_path}/cycle/product/price"


def test_should_run_product():
    product = {'@type': 'Product'}
    assert not _should_run_product(product)

    product['value'] = [1]
    assert _should_run_product(product)

    product['price'] = 2
    assert not _should_run_product(product)


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
