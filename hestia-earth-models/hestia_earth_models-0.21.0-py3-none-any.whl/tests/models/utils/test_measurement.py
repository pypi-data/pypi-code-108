from unittest.mock import patch
import json
from tests.utils import fixtures_path, TERM

from hestia_earth.models.utils.measurement import (
    _new_measurement, most_relevant_measurement_value, _most_recent_measurements, _shallowest_measurement
)

class_path = 'hestia_earth.models.utils.measurement'
fixtures_folder = f"{fixtures_path}/utils/measurement"


@patch(f"{class_path}._include_methodModel", side_effect=lambda n, x: n)
@patch(f"{class_path}._include_source", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_hestia", return_value=TERM)
def test_new_measurement(*args):
    # with a Term as string
    measurement = _new_measurement('term')
    assert measurement == {
        '@type': 'Measurement',
        'term': TERM
    }

    # with a Term as dict
    measurement = _new_measurement(TERM)
    assert measurement == {
        '@type': 'Measurement',
        'term': TERM
    }


def test_most_relevant_measurement_value_single():
    measurements = [
        {
            'term': {
                '@type': 'Term',
                '@id': 'soilPh'
            },
            'value': [
                2000
            ]
        }
    ]

    assert most_relevant_measurement_value(measurements, 'soilPh', '2011') == 2000


def test_most_relevant_measurement_value_by_year():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    assert most_relevant_measurement_value(measurements, 'soilPh', '2011') == 2010


def test_most_relevant_measurement_value_by_year_month():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    assert most_relevant_measurement_value(measurements, 'soilPh', '2001-10') == 2001


def test_most_relevant_measurement_value_by_year_month_day():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    assert most_relevant_measurement_value(measurements, 'soilPh', '2030-01-07') == 2030


def test_most_recent_measurements():
    with open(f"{fixtures_folder}/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    with open(f"{fixtures_folder}/most-recent/measurements.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert _most_recent_measurements(measurements, '2011') == expected


def test_shallowest_measurement():
    with open(f"{fixtures_folder}/most-recent/measurements.jsonld", encoding='utf-8') as f:
        measurements = json.load(f)

    with open(f"{fixtures_folder}/shallowest/measurement.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert _shallowest_measurement(measurements) == expected
