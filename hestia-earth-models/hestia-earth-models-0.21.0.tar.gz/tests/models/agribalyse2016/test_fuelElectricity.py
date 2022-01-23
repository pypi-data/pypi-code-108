from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input
from hestia_earth.schema import TermTermType

from hestia_earth.models.agribalyse2016.fuelElectricity import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.fuelElectricity"
fixtures_folder = f"{fixtures_path}/{MODEL}/fuelElectricity"


def test_should_run():
    # no practices => no run
    cycle = {'practices': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with operation practice => run
    cycle['practices'] = [
        {'term': {'termType': TermTermType.OPERATION.value}, 'value': [10]}
    ]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
