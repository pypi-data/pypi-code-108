from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.ipcc2013IncludingFeedbacks.gwp100 import TERM_ID, run

class_path = f"hestia_earth.models.ipcc2013IncludingFeedbacks.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/ipcc2013IncludingFeedbacks/{TERM_ID}"


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_path}/impact_assessment/emissions/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)
    with open(f"{fixtures_path}/impact_assessment/emissions/result.jsonld", encoding='utf-8') as f:
        emissions = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    impact['emissionsResourceUse'] = emissions
    value = run(impact)
    assert value == expected
