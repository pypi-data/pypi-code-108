from unittest.mock import patch
from tests.utils import TERM

from hestia_earth.models.utils.indicator import _new_indicator

class_path = 'hestia_earth.models.utils.indicator'


@patch(f"{class_path}._include_methodModel", side_effect=lambda n, x: n)
@patch(f"{class_path}.download_hestia", return_value=TERM)
def test_new_indicator(*args):
    # with a Term as string
    indicator = _new_indicator('term')
    assert indicator == {
        '@type': 'Indicator',
        'term': TERM
    }

    # with a Term as dict
    indicator = _new_indicator(TERM)
    assert indicator == {
        '@type': 'Indicator',
        'term': TERM
    }
