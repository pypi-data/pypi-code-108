from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_measurement

from hestia_earth.models.pooreNemecek2018.flowingWater import MODEL, run, _should_run

class_path = f"hestia_earth.models.{MODEL}.flowingWater"
fixtures_folder = f"{fixtures_path}/{MODEL}/flowingWater"


def test_should_run():
    # with an inland siteType => no run
    site = {'siteType': 'cropland'}
    assert not _should_run(site)

    # with a water siteType => run
    site = {'siteType': 'lake'}
    assert _should_run(site) is True


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run(*args):
    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
def test_run_river(*args):
    with open(f"{fixtures_folder}/river/site.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/river/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
