from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.deRuijterEtAl2010.nh3ToAirCropResidueDecomposition import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.deRuijterEtAl2010.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/deRuijterEtAl2010/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}._is_term_type_complete", return_value=False)
@patch(f"{class_path}.abg_residue_nitrogen", return_value=0)
@patch(f"{class_path}.abg_total_residue_nitrogen_content", return_value=0)
def test_should_run(mock_nitrogen_content, mock_abg_residue_nitrogen, mock_data_complete, _m):
    # nitrogen content below 5 => no run
    mock_nitrogen_content.return_value = 1
    should_run, *args = _should_run({})
    assert not should_run

    # nitrogen content above 5 => no run
    mock_nitrogen_content.return_value = 10
    should_run, *args = _should_run({})
    assert not should_run

    # abg residue == 0 => no run
    mock_abg_residue_nitrogen.return_value = 0
    should_run, *args = _should_run({})
    assert not should_run

    # data complete => run
    mock_data_complete.return_value = True
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
def test_run_low_nitrogen_total(*args):
    with open(f"{fixtures_folder}/low-total-nitrogen/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/low-total-nitrogen/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
