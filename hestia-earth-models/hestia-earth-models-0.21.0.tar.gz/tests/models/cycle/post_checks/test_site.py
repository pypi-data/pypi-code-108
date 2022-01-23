import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.post_checks.site import run, _should_run


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
    with open(f"{fixtures_path}/cycle/complete.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    site = cycle.get('site')
    value = run(cycle)
    assert value['site'] == {'@type': site['@type'], '@id': site['@id']}
