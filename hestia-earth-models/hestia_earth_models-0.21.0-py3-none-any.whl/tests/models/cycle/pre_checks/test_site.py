from unittest.mock import patch
from tests.utils import SITE

from hestia_earth.models.cycle.pre_checks.site import run, _should_run

class_path = 'hestia_earth.models.cycle.pre_checks.site'


def test_should_run():
    site = {}
    impact = {'site': site}

    # site has no @id => no run
    assert not _should_run(impact)
    site['@id'] = 'id'

    # site has an @id => run
    assert _should_run(impact)


def test_run_no_site():
    cycle = {}

    value = run(cycle)
    assert 'site' not in value


@patch(f"{class_path}._load_calculated_node", return_value=SITE)
def test_run(*args):
    cycle = {'site': {'@id': SITE['@id']}}

    value = run(cycle)
    assert value['site'] == SITE
