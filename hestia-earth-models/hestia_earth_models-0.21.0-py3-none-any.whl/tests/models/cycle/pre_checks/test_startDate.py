import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.pre_checks.startDate import run, _should_run

fixtures_folder = f"{fixtures_path}/cycle/pre_checks/startDate"


def test_should_run():
    cycle = {}

    # no endDate => no run
    cycle['endDate'] = None
    assert not _should_run(cycle)

    cycle['endDate'] = '2010'
    # no cycleDuration => no run
    cycle['cycleDuration'] = None
    assert not _should_run(cycle)

    cycle['cycleDuration'] = 120
    # with a startDate => no run
    cycle['startDate'] = '2010'
    assert not _should_run(cycle)

    cycle['startDate'] = None
    # endDate not precise enough => no run
    cycle['endDate'] = '2020-01'
    assert not _should_run(cycle)

    # endDate is precise enough => run
    cycle['endDate'] = '2020-01-01'
    assert _should_run(cycle) is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
