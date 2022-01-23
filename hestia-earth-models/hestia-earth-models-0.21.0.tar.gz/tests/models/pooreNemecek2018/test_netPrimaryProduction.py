from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.pooreNemecek2018.netPrimaryProduction import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.pooreNemecek2018.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/pooreNemecek2018/{TERM_ID}"


def test_should_run():
    # no measurements => no run
    site = {'measurements': []}
    should_run, *args = _should_run(site)
    assert not should_run

    # with temperature => run
    site['measurements'].append({
        'term': {
            '@id': 'temperatureAnnual'
        },
        'value': [10]
    })
    should_run, *args = _should_run(site)
    assert should_run is True


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
