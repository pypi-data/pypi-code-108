import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.siteDuration import MODEL, MODEL_KEY, _should_run, run

fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"


def test_should_run():
    # no cycleDuration => no run
    cycle = {}
    should_run = _should_run(cycle)
    assert not should_run

    # with cycleDuration => run
    cycle['cycleDuration'] = 100
    should_run = _should_run(cycle)
    assert should_run is True

    # with otherSites => no run
    cycle['otherSites'] = [{}]
    should_run = _should_run(cycle)
    assert not should_run


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        data = json.load(f)

    with open(f"{fixtures_folder}/result.txt", encoding='utf-8') as f:
        expected = f.read().strip()

    value = run(data)
    assert float(value) == float(expected)
