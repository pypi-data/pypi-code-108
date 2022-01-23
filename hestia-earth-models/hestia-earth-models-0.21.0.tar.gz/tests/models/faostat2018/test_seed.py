from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input

from hestia_earth.models.faostat2018.seed import TERM_ID, _should_run, run

class_path = 'hestia_earth.models.faostat2018.seed'
fixtures_folder = f"{fixtures_path}/faostat2018/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
def test_should_run(mock_is_term_type_incomplete, *args):
    mock_is_term_type_incomplete.return_value = False
    should_run, *args = _should_run({})
    assert not should_run

    mock_is_term_type_incomplete.return_value = True
    should_run, *args = _should_run({})
    assert not should_run

    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run_multi_cropping(*args):
    with open(f"{fixtures_folder}/multi-cropping/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/multi-cropping/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
