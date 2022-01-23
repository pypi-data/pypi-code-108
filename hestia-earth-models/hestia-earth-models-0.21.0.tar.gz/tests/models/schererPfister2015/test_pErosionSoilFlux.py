from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.schererPfister2015.pErosionSoilFlux import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.most_relevant_measurement_value", return_value=0)
@patch(f"{class_path}.get_practice_factor", return_value=0)
@patch(f"{class_path}.get_p_ef_c1", return_value=0)
@patch(f"{class_path}.get_ef_p_c2", return_value=0)
@patch(f"{class_path}.get_pcorr", return_value=0)
def test_should_run(mock_pcorr, mock_ef_p_c2, mock_p_ef_c1, mock_practice_factor, mock_measurement, _m):
    cycle = {
        'inputs': [],
        'measurements': [],
        'site': {
            '@id': '8-gSWoPHEQx',
            '@type': 'Site',
            'siteType': 'cropland',
            'country': {
                '@id': 'GADM-NPL'
            }
        }
    }

    # with a site => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with measurements => no run
    mock_measurement.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with practice_factor => no run
    mock_practice_factor.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with p_ef_c1 => no run
    mock_p_ef_c1.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with ef_p_c2 => no run
    mock_ef_p_c2.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with pcorr => run
    mock_pcorr.return_value = 10
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"hestia_earth.models.{MODEL}.utils.get_tillage_terms", return_value=['fullTillage'])
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
