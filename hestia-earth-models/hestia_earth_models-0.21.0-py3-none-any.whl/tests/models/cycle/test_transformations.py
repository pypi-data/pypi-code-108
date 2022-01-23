import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.transformations import run

fixtures_folder = f"{fixtures_path}/cycle/transformations"


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
