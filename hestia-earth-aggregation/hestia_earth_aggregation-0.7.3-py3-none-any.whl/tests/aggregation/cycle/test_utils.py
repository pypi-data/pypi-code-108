import json

from tests.utils import fixtures_path
from hestia_earth.aggregation.cycle.utils import _aggregate_completeness


def test_aggregate_completeness():
    with open(f"{fixtures_path}/cycle/all.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    with open(f"{fixtures_path}/cycle/utils/dataCompleteness.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert _aggregate_completeness(cycles) == expected
