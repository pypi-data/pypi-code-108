from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.cycle.irrigated import TERM_ID, run, _should_run

class_path = 'hestia_earth.models.cycle.irrigated'
fixtures_folder = f"{fixtures_path}/cycle/{TERM_ID}"


def test_should_run():
    # with irrigation practice => no run
    with open(f"{fixtures_folder}/with-irrigation-practices/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)
    assert not _should_run(cycle)

    # with irrigation input but value too low => no run
    with open(f"{fixtures_folder}/with-irrigation-inputs-low-value/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)
    assert not _should_run(cycle)


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*argsm):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
