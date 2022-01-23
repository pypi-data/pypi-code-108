from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission, FLOODED_RICE_TERMS
from hestia_earth.utils.model import find_primary_product
from hestia_earth.models.utils.property import get_node_property

from hestia_earth.models.pooreNemecek2018.no3ToGroundwaterSoilFlux import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.pooreNemecek2018.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/pooreNemecek2018/{TERM_ID}"


def primary_rooting_depth(cycle: dict):
    return get_node_property(find_primary_product(cycle), 'rootingDepth').get('value')


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.most_relevant_measurement_value", return_value=0)
@patch(f"{class_path}.get_max_rooting_depth", return_value=0)
def test_should_run(mock_rooting_depth, mock_measurement, _m):
    # no measurements => no run
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with measurements => no run
    mock_measurement.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # no rootingDepth => no run
    should_run, *args = _should_run({})
    assert not should_run

    # with rootingDepth => run
    mock_rooting_depth.return_value = 10
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}.get_max_rooting_depth", side_effect=primary_rooting_depth)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_max_rooting_depth", side_effect=primary_rooting_depth)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_high_conditions(*args):
    with open(f"{fixtures_folder}/with-high-conditions/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-high-conditions/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_max_rooting_depth", side_effect=primary_rooting_depth)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_low_conditions(*args):
    with open(f"{fixtures_folder}/with-low-conditions/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-low-conditions/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}.get_rice_paddy_terms", return_value=FLOODED_RICE_TERMS)
@patch(f"{class_path}.get_max_rooting_depth", side_effect=primary_rooting_depth)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_flooded_rice(*args):
    with open(f"{fixtures_folder}/with-flooded-rice/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-flooded-rice/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
