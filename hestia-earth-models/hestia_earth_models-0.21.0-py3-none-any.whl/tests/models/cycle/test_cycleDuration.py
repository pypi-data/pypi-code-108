from unittest.mock import patch
import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.cycleDuration import MODEL, MODEL_KEY, _should_run, run

class_path = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.most_relevant_measurement_value", return_value=0)
def test_should_run(mock_measurement, *args):
    # no cycleDuration => no run
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with cycleDuration = 100 => no run
    cycle['cycleDuration'] = 100
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with measurement => no run
    mock_measurement.return_value = 100
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with cycleDuration = 365 => run
    cycle['cycleDuration'] = 365
    should_run, *args = _should_run(cycle)
    assert should_run is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    result = run(data)
    assert float(result) == float(expected)
