from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.spatial.histosol import TERM_ID, _should_run, run

class_path = f"hestia_earth.models.spatial.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/spatial/{TERM_ID}"


@patch(f"{class_path}.has_geospatial_data", return_value=True)
def test_should_run(*args):
    # with no soilType => run
    site = {'measurements': []}
    assert _should_run(site) is True

    # with an existing soilType => NO run
    with open(f"{fixtures_folder}/with-soilType.jsonld", encoding='utf-8') as f:
        site = json.load(f)
    assert not _should_run(site)


@patch(f"{class_path}.find_existing_measurement", return_value=None)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run_coordinates(*args):
    with open(f"{fixtures_folder}/coordinates.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}.find_existing_measurement", return_value=None)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run_boundary(*args):
    with open(f"{fixtures_folder}/boundary.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
