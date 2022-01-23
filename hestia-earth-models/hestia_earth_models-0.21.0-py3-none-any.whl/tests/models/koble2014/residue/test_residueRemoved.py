import json
from tests.utils import fixtures_path

from hestia_earth.models.koble2014.residue.residueRemoved import run

fixtures_folder = f"{fixtures_path}/koble2014/residue"


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    primary_product = cycle.get('products')[0]
    assert run(cycle, primary_product) == 20
