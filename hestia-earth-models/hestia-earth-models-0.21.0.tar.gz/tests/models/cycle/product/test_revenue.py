import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.revenue import MODEL_KEY, run, _should_run

class_path = f"hestia_earth.models.cycle.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/cycle/product/{MODEL_KEY}"


def test_should_run():
    product = {'@type': 'Product'}
    assert not _should_run(product)

    product['value'] = [0]
    assert _should_run(product) is True

    product['value'] = [1]
    assert not _should_run(product)

    product['price'] = 1
    assert _should_run(product) is True

    product['revenue'] = 2
    assert not _should_run(product)


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
