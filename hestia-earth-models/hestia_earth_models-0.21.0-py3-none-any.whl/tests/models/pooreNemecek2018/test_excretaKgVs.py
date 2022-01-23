from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.pooreNemecek2018.excretaKgVs import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.excretaKgVs"
fixtures_folder = f"{fixtures_path}/{MODEL}/excretaKgVs"


@patch(f"{class_path}._get_excreta_n_term", return_value='')
@patch(f"{class_path}.get_excreta_terms", return_value=[])
@patch(f"{class_path}.get_feed_carbon", return_value=5)
@patch(f"{class_path}._get_carbonContent", return_value=5)
@patch(f"{class_path}._get_conv_aq_ocsed", return_value=0.35)
@patch(f"{class_path}._get_excreta_vs_term", return_value='excretaKgVs')
@patch(f"{class_path}.most_relevant_measurement_value", return_value=5)
def test_should_run(*args):
    cycle = {'practices': []}

    # no practices => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # dataCompleteness False => no run
    cycle['dataCompleteness'] = {
        'animalFeed': False,
        'products': False
    }
    should_run, *args = _should_run(cycle)
    assert not should_run

    # dataCompleteness True => no run
    cycle['dataCompleteness'] = {
        'animalFeed': True,
        'products': True
    }
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with yts => no run
    cycle['practices'].append({
        'term': {
            '@id': 'yieldOfPrimaryAquacultureProductLiveweightPerM2'
        },
        'value': [
            0.243948562783661
        ]
    })
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with slaughterAge => run
    cycle['practices'].append({
        'term': {
            '@id': 'slaughterAge'
        },
        'value': [
            333
        ]
    })
    should_run, *args = _should_run(cycle)
    assert should_run is True


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
def test_run_excretaKgN(*args):
    with open(f"{fixtures_folder}/with-excretaKgN/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-excretaKgN/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
