from unittest.mock import patch
from hestia_earth.schema import SchemaType
from tests.utils import CYCLE, SITE

from hestia_earth.models.impact_assessment.pre_checks.cycle import run, _should_run

class_path = 'hestia_earth.models.impact_assessment.pre_checks.cycle'


def fake_load_calculated_node(node, type):
    return {**CYCLE} if type == SchemaType.CYCLE else {**SITE}


def test_should_run():
    cycle = {}
    impact = {'cycle': cycle}

    # cycle has no @id => no run
    assert not _should_run(impact)
    cycle['@id'] = 'id'

    # cycle has an @id => run
    assert _should_run(impact)


def test_run_no_cycle():
    impact = {}

    value = run(impact)
    assert 'cycle' not in value


@patch(f"{class_path}._load_calculated_node", side_effect=fake_load_calculated_node)
def test_run(*args):
    impact = {'cycle': {'@id': CYCLE['@id']}}

    value = run(impact)
    # loads the cycle and the site
    assert value['cycle'] == {**CYCLE, 'site': SITE}
