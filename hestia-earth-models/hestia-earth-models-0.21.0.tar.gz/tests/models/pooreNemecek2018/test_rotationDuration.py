from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.pooreNemecek2018.rotationDuration import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
def test_should_run(mock_is_term_type_incomplete, _m):
    mock_is_term_type_incomplete.return_value = False
    assert not _should_run({})

    mock_is_term_type_incomplete.return_value = True
    assert _should_run({}) is True


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_no_orchard_crop(*args):
    with open(f"{fixtures_folder}/no-orchard-crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []
