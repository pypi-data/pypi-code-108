from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.ch4ToAirExcreta import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.find_primary_product", return_value={'term': {'@id': 'primary'}})
@patch(f"{class_path}._get_ch4_conv_factor", return_value=None)
@patch(f"{class_path}._get_ch4_potential", return_value=None)
def test_should_run(mock_ch4_potential, mock_ch4_conv, *args):
    cycle = {}

    # no practices => no run
    cycle['practices'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # no products => no run
    cycle['products'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # no inputs => no run
    cycle['inputs'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    mock_ch4_potential.return_value = 10
    mock_ch4_conv.return_value = 10
    cycle['inputs'] = [
        {
            'term': {
                '@id': 'excretaKgVs',
                'termType': 'excreta',
                'units': 'kg VS'
            },
            'value': [10]
        }
    ]

    # with excretaKgVs => run
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
