from unittest.mock import patch
from tests.utils import SITE

from hestia_earth.models.impact_assessment.pre_checks.site import run, _should_run

class_path = 'hestia_earth.models.impact_assessment.pre_checks.site'


def fake_load_calculated_node(*args): return {**SITE}


def test_should_run():
    site = {}
    impact = {'site': site}

    # site has no @id => no run
    assert not _should_run(impact)
    site['@id'] = 'id'

    # site has an @id => run
    assert _should_run(impact)


def test_run_no_site():
    impact = {}

    value = run(impact)
    assert 'site' not in value


@patch(f"{class_path}._load_calculated_node", side_effect=fake_load_calculated_node)
def test_run(*args):
    impact = {'site': {'@id': SITE['@id']}}

    value = run(impact)
    # loads the site and the site
    assert value['site'] == SITE
