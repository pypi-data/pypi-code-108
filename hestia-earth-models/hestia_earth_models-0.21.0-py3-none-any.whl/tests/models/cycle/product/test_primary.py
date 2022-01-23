import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.primary import MODEL_KEY, run, _should_run, _run

class_path = f"hestia_earth.models.cycle.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/cycle/product/{MODEL_KEY}"


def test_should_run():
    # no products => do not run
    products = []
    assert not _should_run(products)

    # with product but no primary info => run
    product = {
        '@type': 'Product'
    }
    products.append(product)
    assert _should_run(products) is True

    # with product with primary => no run
    product['primary'] = True
    assert not _should_run(products)


def test__run():
    # only 1 product => primary
    products = [{
        '@type': 'Product',
        'term': {
            '@id': 'product-1'
        }
    }]
    assert _run(products)[0].get('term').get('@id') == 'product-1'

    # multiple products => primary with biggest economicValueShare
    products = [{
        '@type': 'Product',
        'term': {
            '@id': 'product-1'
        },
        'economicValueShare': 100
    }, {
        '@type': 'Product',
        'term': {
            '@id': 'product-2'
        },
        'economicValueShare': 0
    }, {
        '@type': 'Product',
        'term': {
            '@id': 'product-3'
        },
        'economicValueShare': 456464564
    }, {
        '@type': 'Product',
        'term': {
            '@id': 'product-4'
        }
    }]
    assert _run(products)[0].get('term').get('@id') == 'product-3'


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
