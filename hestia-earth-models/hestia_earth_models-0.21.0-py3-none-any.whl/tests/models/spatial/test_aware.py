from unittest.mock import patch
import json
from tests.utils import fixtures_path

from hestia_earth.models.spatial.aware import _should_run, run

class_path = 'hestia_earth.models.spatial.aware'
fixtures_folder = f"{fixtures_path}/spatial/aware"


@patch(f"{class_path}.has_geospatial_data")
def test_should_run(mock_has_geospatial_data):
    mock_has_geospatial_data.return_value = True
    assert _should_run({}) is True

    mock_has_geospatial_data.return_value = False
    assert not _should_run({})


def test_run_boundary():
    with open(f"{fixtures_path}/spatial/boundary.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    result = run(site)
    assert result == expected


def test_run_coordinates():
    with open(f"{fixtures_path}/spatial/coordinates.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    result = run(site)
    assert result == expected
