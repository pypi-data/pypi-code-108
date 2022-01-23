from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_input
from hestia_earth.schema import SiteSiteType

from hestia_earth.models.agribalyse2016.machineryInfrastructureDepreciatedAmountPerCycle import (
    MODEL, TERM_ID, run, _should_run
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"
TERMS = [
    'diesel'
]


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
def test_should_run(*args):
    cycle = {'site': {}}
    assert not _should_run(cycle)

    cycle['site']['siteType'] = SiteSiteType.CROPLAND.value
    assert _should_run(cycle) is True


@patch(f"{class_path}.get_liquid_fuel_terms", return_value=TERMS)
@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_input", side_effect=fake_new_input)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
