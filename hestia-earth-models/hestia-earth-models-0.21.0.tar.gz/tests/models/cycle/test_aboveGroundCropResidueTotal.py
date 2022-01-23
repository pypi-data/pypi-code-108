from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.cycle.aboveGroundCropResidueTotal import MODEL, TERM_ID, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}.find_term_match")
def test_should_run(mock_find, *args):
    # no practice or product => no run
    mock_find.return_value = {}
    should_run, *args = _should_run({})
    assert not should_run

    # with practice and product => run
    mock_find.return_value = {'value': [10]}
    should_run, *args = _should_run({})
    assert should_run is True


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
