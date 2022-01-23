from unittest.mock import patch
import json
from hestia_earth.utils.tools import non_empty_list
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.otherBackgroundDatabase import MODEL, run

class_path = f"hestia_earth.models.{MODEL}"
fixtures_folder = f"{fixtures_path}/{MODEL}"


def fake_load_impacts(inputs):
    def _load_impact(input: dict):
        impact = input.get('impactAssessment')
        if impact:
            with open(f"{fixtures_path}/impact_assessment/{impact.get('@id')}.jsonld", encoding='utf-8') as f:
                return {**input, 'impactAssessment': json.load(f)}
    return non_empty_list(map(_load_impact, inputs))


@patch(F"{class_path}.load_impacts", side_effect=fake_load_impacts)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run('all', cycle)
    assert result == expected
