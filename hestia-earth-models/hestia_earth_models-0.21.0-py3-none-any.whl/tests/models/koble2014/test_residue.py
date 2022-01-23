from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.koble2014.residue import run, _should_run, _should_run_model

class_path = 'hestia_earth.models.koble2014.residue'
fixtures_folder = f"{fixtures_path}/koble2014/residue"


def test_should_run_model():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    term_id = cycle['practices'][0]['term']['@id']
    assert not _should_run_model(term_id, cycle)

    term_id = 'random term'
    assert _should_run_model(term_id, cycle)


@patch(f"{class_path}.find_primary_product")
def test_should_run(mock_primary_product):
    # no primary product => no run
    mock_primary_product.return_value = None
    should_run, *args = _should_run({})
    assert not should_run

    # with primary product => run
    mock_primary_product.return_value = {}
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
