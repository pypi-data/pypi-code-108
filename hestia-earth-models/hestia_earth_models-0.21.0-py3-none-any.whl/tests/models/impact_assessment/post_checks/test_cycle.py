import json
from tests.utils import fixtures_path

from hestia_earth.models.impact_assessment.post_checks.cycle import run, _should_run


def test_should_run():
    cycle = {}
    impact = {'cycle': cycle}

    # cycle has no @id => no run
    assert not _should_run(impact)
    cycle['@id'] = 'id'

    # cycle has an id => run
    assert _should_run(impact)


def test_run():
    # contains a full cycle
    with open(f"{fixtures_path}/impact_assessment/complete.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    cycle = impact.get('cycle')
    value = run(impact)
    assert value['cycle'] == {'@type': cycle['@type'], '@id': cycle['@id']}
