from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.site.measurement.value import run, _should_run

class_path = 'hestia_earth.models.site.measurement.value'
fixtures_folder = f"{fixtures_path}/site/measurement/value"


def test_should_run():
    measurement = {}

    # without min/max => NO run
    assert not _should_run(measurement)

    # with min and max and value => NO run
    measurement = {
        'min': [5],
        'max': [50],
        'value': [25]
    }
    assert not _should_run(measurement)

    # with min and max but not value => run
    measurement = {
        'min': [5],
        'max': [10],
        'value': []
    }
    assert _should_run(measurement) is True


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
