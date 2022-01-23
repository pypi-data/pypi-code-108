import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.value import run, _should_run

class_path = 'hestia_earth.models.cycle.product.value'
fixtures_folder = f"{fixtures_path}/cycle/product/value"


def test_should_run():
    product = {}

    # without min/max => NO run
    assert not _should_run(product)

    # with min and max and value => NO run
    product = {
        'min': [5],
        'max': [50],
        'value': [25]
    }
    assert not _should_run(product)

    # with min and max but not value => run
    product = {
        'min': [5],
        'max': [10],
        'value': []
    }
    assert _should_run(product)


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
