from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.stehfestBouwman2006GisImplementation.noxToAirInorganicFertilizer import TERM_ID, run

class_path = f"hestia_earth.models.stehfestBouwman2006GisImplementation.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/stehfestBouwman2006GisImplementation/{TERM_ID}"


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_data_complete(*args):
    with open(f"{fixtures_path}/stehfestBouwman2006GisImplementation/data-complete/cycle.jsonld",
              encoding='utf-8') as f:
        cycle = json.load(f)

    expected = []
    value = run(cycle)
    assert value == expected
