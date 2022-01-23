from unittest.mock import patch
from tests.utils import TERM

from hestia_earth.models.utils.property import _new_property


@patch('hestia_earth.models.utils.property._include_methodModel', side_effect=lambda n, x: n)
@patch('hestia_earth.models.utils.property.download_hestia', return_value=TERM)
def test_new_property(*args):
    # with a Term as string
    property = _new_property('term')
    assert property == {
        '@type': 'Property',
        'term': TERM
    }

    # with a Term as dict
    property = _new_property(TERM)
    assert property == {
        '@type': 'Property',
        'term': TERM
    }
