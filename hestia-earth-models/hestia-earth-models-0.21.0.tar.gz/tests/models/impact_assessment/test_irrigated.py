import json
from tests.utils import fixtures_path

from hestia_earth.models.impact_assessment.irrigated import MODEL_KEY, run

fixtures_folder = f"{fixtures_path}/impact_assessment/{MODEL_KEY}"


def test_run():
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    value = run(impact)
    assert value is True
