from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.akagiEtAl2011AndIpcc2006.ch4ToAirCropResidueBurning import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.akagiEtAl2011AndIpcc2006.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/akagiEtAl2011AndIpcc2006/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}._get_aboveGroundCropResidueBurnt_value")
def test_should_run(mock_product_value, *args):
    # no products => no run
    mock_product_value.return_value = []
    should_run, *args = _should_run({})
    assert not should_run

    # with products => run
    mock_product_value.return_value = [0]
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_data_complete(*args):
    with open(f"{fixtures_folder}/no-product-data-complete/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/no-product-data-complete/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
