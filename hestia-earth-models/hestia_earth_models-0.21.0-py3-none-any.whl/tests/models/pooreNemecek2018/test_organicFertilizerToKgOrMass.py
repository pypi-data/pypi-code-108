from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input, order_list

from hestia_earth.models.pooreNemecek2018.organicFertilizerToKgOrMass import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.organicFertilizerToKgOrMass"
fixtures_folder = f"{fixtures_path}/{MODEL}/organicFertilizerToKgOrMass"


@patch(f"{class_path}.node_exists")
def test_should_run(mock_node_exists):
    # no inputs => no run
    inputs = []
    should_run, term_ids = _should_run(inputs)
    assert not should_run

    term_id = 'term'
    inputs.append({
        'term': {
            '@id': term_id + 'KgN'
        },
        'value': 0.00208
    })

    # with input and existing KgMass => no run
    mock_node_exists.return_value = False
    should_run, term_ids = _should_run(inputs)
    assert not should_run

    # with input and non-existing KgMass => run
    mock_node_exists.return_value = True
    should_run, term_ids = _should_run(inputs)
    assert term_ids == [term_id]
    assert should_run is True


def fake_node_exists(id: str):
    return id in [
        'beefCattleSolidManureFreshKgN', 'beefCattleSolidManureFreshKgMass',
        'manureFreshKgN', 'manureFreshKgMass'
    ]


def fake_find_term_property(term_id, *args):
    return {'value': 0.52 if term_id == 'beefCattleSolidManureFreshKgMass' else 0.529724771}


@patch(f"{class_path}.find_term_property", side_effect=fake_find_term_property)
@patch(f"{class_path}.node_exists", side_effect=fake_node_exists)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    # cycle with an organic fertiliser => Iranian Hazelnut example
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert order_list(value) == order_list(expected)
