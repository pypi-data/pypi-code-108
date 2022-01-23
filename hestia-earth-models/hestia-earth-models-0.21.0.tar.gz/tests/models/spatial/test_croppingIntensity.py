from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.spatial.croppingIntensity import TERM_ID, _should_run, run

class_path = f"hestia_earth.models.spatial.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/spatial/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.has_geospatial_data")
def test_should_run(mock_has_geospatial_data, *args):
    mock_has_geospatial_data.return_value = True
    assert _should_run({}) is True

    mock_has_geospatial_data.return_value = False
    assert not _should_run({})


@patch(f"{class_path}.find_existing_measurement", return_value=None)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run_coordinates(*args):
    with open(f"{fixtures_path}/spatial/coordinates.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}.find_existing_measurement", return_value=None)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run_boundary(*args):
    with open(f"{fixtures_path}/spatial/boundary.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/boundary/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
