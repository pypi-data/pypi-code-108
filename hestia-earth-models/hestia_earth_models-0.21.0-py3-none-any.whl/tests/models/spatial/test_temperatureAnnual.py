from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.spatial.temperatureAnnual import TERM_ID, _should_run, run

class_path = f"hestia_earth.models.spatial.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/spatial/{TERM_ID}"


def fake_cycles(*args): return [{'@id': 'id', 'endDate': '2009'}]


@patch(f"{class_path}.has_geospatial_data")
def test_should_run(mock_has_geospatial_data):
    mock_has_geospatial_data.return_value = True

    site = {}
    end_year = 1978

    # end date too far => NO run
    assert not _should_run(site, end_year)

    # end date not too far => run
    end_year = 1990
    assert _should_run(site, end_year)


@patch(f"{class_path}.find_existing_measurement", return_value=None)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.related_cycles", side_effect=fake_cycles)
def test_run_coordinates(*args):
    with open(f"{fixtures_path}/spatial/coordinates.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}.find_existing_measurement", return_value=None)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.related_cycles", side_effect=fake_cycles)
def test_run_boundary(*args):
    with open(f"{fixtures_path}/spatial/boundary.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/boundary/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
