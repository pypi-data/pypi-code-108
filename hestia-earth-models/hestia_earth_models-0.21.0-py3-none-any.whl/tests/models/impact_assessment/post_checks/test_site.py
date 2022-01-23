import json
from tests.utils import fixtures_path

from hestia_earth.models.impact_assessment.post_checks.site import run, _should_run


def test_should_run():
    site = {}
    impact = {'site': site}

    # site has no @id => no run
    assert not _should_run(impact)
    site['@id'] = 'id'

    # site has an id => run
    assert _should_run(impact)


def test_run():
    # contains a full site
    with open(f"{fixtures_path}/impact_assessment/complete.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    site = impact.get('site')
    value = run(impact)
    assert value['site'] == {'@type': site['@type'], '@id': site['@id']}
