from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.pooreNemecek2018.excretaKgN import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.excretaKgN"
fixtures_folder = f"{fixtures_path}/{MODEL}/excretaKgN"


@patch(f"{class_path}._get_nitrogen_content", return_value=10)
@patch(f"{class_path}.get_excreta_terms", return_value=[])
@patch(f"{class_path}.get_feed_nitrogen", return_value=0)
@patch(f"{class_path}.animal_produced", return_value=0)
@patch(f"{class_path}._get_excreta_n_term", return_value='excretaKgN')
def test_should_run(mock_get_excreta_term, mock_animal_produced, mock_get_feed, *args):
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # dataCompleteness False => no run
    cycle = {
        'dataCompleteness': {
            'animalFeed': False,
            'products': False
        }
    }
    mock_get_feed.return_value = 0
    mock_animal_produced.return_value = 0
    should_run, *args = _should_run(cycle)
    assert not should_run

    # dataCompleteness True => run
    cycle = {
        'dataCompleteness': {
            'animalFeed': True,
            'products': True
        }
    }
    mock_get_feed.return_value = 5
    mock_animal_produced.return_value = 5
    should_run, *args = _should_run(cycle)
    assert should_run is True

    # no excreta term => no run
    mock_get_excreta_term.return_value = None
    should_run, *args = _should_run(cycle)
    assert not should_run

    # excreta already present => no run
    cycle['products'] = [
        {
            'term': {
                '@id': 'excretaKgN'
            }
        }
    ]
    should_run, *args = _should_run(cycle)
    assert not should_run


@patch(f"{class_path}.get_excreta_terms", return_value=[])
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_excreta_terms", return_value=[])
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_liveweight(*args):
    with open(f"{fixtures_folder}/with-liveweight/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-liveweight/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_excreta_terms", return_value=[])
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_carcass(*args):
    with open(f"{fixtures_folder}/with-carcass/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-carcass/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_excreta_terms", return_value=[])
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_with_liveAquaticSpecies(*args):
    with open(f"{fixtures_folder}/with-liveAquaticSpecies/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-liveAquaticSpecies/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
